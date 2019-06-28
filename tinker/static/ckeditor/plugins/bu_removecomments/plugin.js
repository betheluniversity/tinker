// The regex used below checks for html comments in the form <!--asdf--> and also takes into account newlines and
// the html encoding of the "<" and ">" characters. The question mark is needed so that if there are multiple html
// comments with data in between we don't lose that data.
CKEDITOR.plugins.add('bu_removecomments', {
    init: function (editor) {
        // This runs when the editor is initialized. This is needed for editing existing faculty bios
        var text = editor.getData();
        text = text.replace(/(<|&lt;)!--((.|\n)*?)--(>|&gt;)/g, "");
        editor.setData(text);

        // This checks content on paste, needed for editing or creating new faculty bios
        editor.on('paste', function(){
            setTimeout(function(){ // Need a timeout so the paste is registered before we change any data.
                var text = editor.getData();
                text = text.replace(/(<|&lt;)!--((.|\n)*?)--(>|&gt;)/g, "");
                editor.setData(text);
            }, 100);
        });
    }
});
