#import tweepy
import pandas as pd
import random
import requests
import time

bearer='AAAAAAAAAAAAAAAAAAAAAJtrMAEAAAAA1lcRQwN%2F42d1PQra0VcVZtt%2FNUc%3D6xX4xjDjpVmzEKgxABYCRXduaFpbtw9KZnLwSxYGWWr5Mz1Qz7'
medias=['OANN']
headers = {'Authorization': 'Bearer %s' % bearer}

print("noi")
user_ids=[]
for media in medias:
    url_timeline=f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={media}&count=200"
    response=requests.get(url_timeline,headers=headers)
    if response.status_code==200:
        tweets=response.json()
        for i in range(len(tweets)):
            tweet=tweets[i]
            if tweet["retweet_count"]>20:
                idx=tweet["id"]
                url_retweeters=f"https://api.twitter.com/1.1/statuses/retweeters/ids.json?id={idx}&count=100"
                response2=requests.get(url_retweeters,headers=headers)
                if response2.status_code==200:
                    response2=response2.json()
                    retweeters=random.choices(response2["ids"],k=20) if len(response2["ids"])>=20 else response2["ids"]
                    user_ids.extend(list(zip(retweeters,[media]*len(retweeters))))
                    print("still first")
                else:
                    if response.status_code==429:
                        time.sleep(3*60)
                        i-=1
                    print(response2.status_code,"retweeters",i)
                    
    else:
        print(response.status_code)
        if response.status_code==429:
            time.sleep(3*60)
print("first done")
time.sleep(3*60)
print("started second")
user_ids=list(set(user_ids))      
users_info={}
for i in range(len(user_ids)):
    useridx,media=user_ids[i]
    url_timeline=f"https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={useridx}&count=200&tweet_mode=extended"
    response=requests.get(url_timeline,headers=headers)
    if response.status_code==200:
        tweets=response.json()
        posts=[]
        for tweet in tweets:
            if "retweeted_status" in tweet.keys():
                text=tweet["retweeted_status"]["full_text"]
            else:
                text = tweet["full_text"]
            posts.append(text)
        bio=tweet["user"]["description"]
        location=tweet["user"]["location"]
        users_info[useridx]={"user_id":useridx,"bio":bio,"location":location,"media":media,"tweets":posts}
        print("still second")
    else:
        print(response.status_code,i)
        if response.status_code==429:
            time.sleep(4*60)
            i-=1
print("second done")
        
import pickle
filehandler = open(f"twitter_{media}.pt", 'wb')
pickle.dump(users_info, filehandler)
filehandler.close()