CKEDITOR.plugins.add('bu_removecomments', {
    init: function (editor) {
        // This runs when the editor is initialized. This is needed for editing existing faculty bios
        var text = editor.getData();
        text = text.replace(/<!--(.*?)-->/gs, "");
        editor.setData(text);

        // This checks content on paste, needed for editing or creating new faculty bios
        editor.on('paste', function(){
            setTimeout(function(){ // Need a timeout so the paste is registered before we change any data.
                var text = editor.getData();
                text = text.replace(/<!--(.*?)-->/gs, "");
                editor.setData(text);
            }, 100);
        });
    }
});