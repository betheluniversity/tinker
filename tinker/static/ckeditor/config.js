/**
 * @license Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
		config.toolbarGroups = [
			{ name: 'clipboard', groups: [ 'undo', 'clipboard' ] },
			{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
			{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
			{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
			{ name: 'links', groups: [ 'links' ] },
			{ name: 'insert', groups: [ 'insert' ] },
			{ name: 'forms', groups: [ 'forms' ] },
			{ name: 'tools', groups: [ 'tools' ] },
			{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
			{ name: 'others', groups: [ 'others' ] },
			{ name: 'styles', groups: [ 'styles' ] },
			{ name: 'colors', groups: [ 'colors' ] },
			{ name: 'about', groups: [ 'about' ] }
		];
		CKEDITOR.config.removeButtons = 'Underline,Subscript,Superscript,Undo,Redo,Cut,Copy,Paste,PasteText,PasteFromWord,Scayt,Strike,RemoveFormat,Blockquote,Anchor,Image,Table,HorizontalRule,SpecialChar,Maximize,Source,Styles';
		CKEDITOR.config.entities = false;
		CKEDITOR.config.extraPlugins = 'bu_removecomments';
};

// i am not sure this works, but it is difficult to actually test. In theory, this should prevent html comments
// from being sent to cascade. I am taking a gamble in hoping this fixes the junk that gets sent - caleb
CKEDITOR.replaceAll( 'ckeditor', {
    on: {
        pluginsLoaded: function( evt ) {
            evt.editor.dataProcessor.dataFilter.addRules( {
                comment: function() {
                    return false;
                }
            } );
        }
    }
} );
