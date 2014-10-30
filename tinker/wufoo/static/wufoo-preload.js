jQuery(document).ready(function($) {
var
    fieldcont = $('#wufoo-form-fields'),
    paypal = $('#wufoo-form-paypal'),
    preloader = $(document.createElement('select')),
    publicReserved = {'EntryId':1,
                        'UpdatedBy':1,
                        'LastUpdated':1,
                        'CreatedBy':1,
                        'DateCreated':1};

var delay = (function(){
  var timer = 50;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

preloader.hide();
preloader.attr("size","1");
preloader.append("<option value=''> -- </option>");
fieldcont.append(preloader);

// JSON call to get the preload options
//   on response fill in the `preloader` select box
$.getJSON('/wufoo/get-preload-options', function(data) {
  preloadOptions = data,
  preloadOptions_loaded = true;
  common = data['common'];
  rare = data['rare'];
  //build the preloader field
  for (var f in common) {
    preloader.append("<option value='"+f+"'>"+common[f]+"</options>");
  }
  //build the preloader field
  for (var f in rare) {
    preloader.append("<option value='"+f+"'>"+rare[f]+"</options>");
  }
});


var getJsonData = function(){
    var url = '/wufoo/get-forms';
    $.getJSON(url, function(data) {
        localStorage.setItem("jsonforms", JSON.stringify(data));
    });
};

var clear = function(){

    $("#wufoo-form-hash").find('option').remove();
};

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

/* generate the DOM for a row in the field mapping form. */
printFieldMap = function(field, dom, preloadData, labelattr, iterate) {
  /* generate the DOM for a row in the field mapping form.
     @field - the JSON field structure
     @dom - the container to place the row in
     @preloadData - the hash of field:preload mapping data
     @labelattr - the attribute in the JSON field structure containing the
                  label (this is different for some types of fields)
     @iterate - an optional class name (e.g. even or odd) to add to the field's
                containing div (used in subfields)
  */

  if (!labelattr) labelattr = 'Title';
  var sel = preloader.clone(),
     fieldid = field['ID'],
      div = $(document.createElement('div')),
      className = 'wufoo-field-item' + iterate?' ' + iterate : '';
  div.attr('class', className);
  div.append(field[labelattr]);
  /* set the value of the select if the field is in the preloadData */
  if (preloadData && preloadData[fieldid]) {
    sel.val(preloadData[fieldid])
  }
  sel.attr('id', fieldid);
  sel.attr('name', fieldid);
  sel.show();
  div.append(sel);
  dom.append(div);
};


function loadFormPreloads(data){
    //clear out the old junk
    $("#preload-config").empty();
    var form_info = data['info'];
    if (form_info)
        preloadData = jQuery.parseJSON(form_info['preload_info']);
    else
        preloadData = null;
    form = jQuery.parseJSON(data['form']);
    var   d = document,
          df = d.createDocumentFragment(),
         div = d.createElement('div'),
      fields = form['Fields'],
        first_fancy = true,
           C = 0;

    df.appendChild(div);
    var dom = $(div);
    dom.append('<h3>Preload Mappings</h3>');
    for (var f in fields) {
      var field = fields[f];
      // display neither reserved fields (automatically added to wufoo forms)
      // nor system fields.
      if (publicReserved[field['ID']] || field['isSystem'])
        continue;
      var block = $(d.createElement('div'));
      var append_str = "";
      var className = "wufoo-field " + ((C++)%2 ? 'even' : 'odd' );
      if (field['SubFields']) {
        if (field['Type'] == 'checkbox') {
          block.append("<fieldset><legend>" + field["Title"] + "</legend><div>Checkbox -- no preload available</div></fieldset");
        } else {

          className += " fancy";

          var fieldset = $(d.createElement('fieldset'));
          fieldset.append("<legend>"+field['Title']+"</legend>");

          var IC = 0;
          for (var s in field['SubFields']) {
            var subfield = field['SubFields'][s];
            printFieldMap(subfield, fieldset, preloadData, "Label", ((IC++)%2?'even':'odd'));
          }
          //all the fields are in, append
          block.append(fieldset);
        }
      } else {
        printFieldMap(field, block, preloadData);
      }
      //apend then final fieldset
      block.attr("class", className);
      dom.append(block);
    }
    var input = $(d.createElement('input'));
    input.attr('value', 'Save');
    input.attr('type', 'button');
    input.attr('class', 'button postfix');
    input.click(function(event) {
      // when 'save' is clicked, gather the field mappings and send those
      // to the wufoo-silva app for storage
      var fieldMappings = $(this.form).serializeArray(),
           url = '/wufoo/preload-save';
      $.post(url,
            fieldMappings
      );
    });
    dom.append(input);
    $("#preload-config").append(df);

}

window.onload = function() {
    $('#wufoo-dropdown-limit').keyup(function() {
        delay(function(){
            clear();
            populate();
        });
    });

    $("#wufoo-form-hash").change(function(){
        var selected = $(this).val();
        var values = selected.split(":"),
            hash = values[0],
            id = values[1];
        //Load the form from the API
        var url = '/wufoo/load-form/' + hash;
        $.getJSON(url, function(data) {
            loadFormPreloads(data);
        });
    });

    //populate the json data
    getJsonData();
    //clear();
    //populate the initial list
    populate();
}


}); // End the veeeery top