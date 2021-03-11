displayFilesList()
  function displayFilesList(){
    var wrapper=document.getElementById('list-wrapper')
    wrapper.innerHTML=''
    var list ={{dataKey|safe}}
    console.log(list)
    for(var i in list){
      var item=`
      <div class="jumbotron">
      <p>${list[i].file_id}</p>
      <p>${list[i].name}</p>
      <p>${list[i].size}</p>
      <p>${list[i].url}</p>
      </div>
      `
      wrapper.innerHTML+=item
    }
}
