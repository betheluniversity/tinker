CKEDITOR.plugins.add('bu_removecomments', {
    init: function (editor) {
        var text = editor.getData();
        text = text.replace(/<!--(.*?)-->/gs, "");
        editor.setData(text);
    }
});