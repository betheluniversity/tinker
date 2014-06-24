var delay = (function(){
  var timer = 50;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();


var getJsonData = function(){
    var url = '/admin/get-forms';
    $.getJSON(url, function(data) {
        localStorage.setItem("jsonforms", JSON.stringify(data));
    });
}

var clear = function(){

    $("#wufoo-form-hash").find('option').remove();
}

var populate = function(){

    var data = JSON.parse(localStorage.getItem("jsonforms"));
    var forms = data['Forms'];
    var limit_text = $("#wufoo-dropdown-limit").val();
    for (var f in forms) {
    var hash = forms[f]['Hash'],
         name = forms[f]['Name'],
         url = forms[f]['Url'];
    var match = name.toLowerCase().indexOf(limit_text.toLowerCase());
    if(match > -1){
        $("#wufoo-form-hash").append("<option value='"+hash+':'+url+"'>"+name+ "(" + url + ")</options>");
    }
    }
};



window.onload = function() {
    $('#wufoo-dropdown-limit').keyup(function() {
        delay(function(){
            clear();
            populate();
        });
    });
    //populate the json data
    getJsonData();
    //clear();
    //populate the initial list
    populate();
}