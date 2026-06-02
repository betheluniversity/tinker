function setMultiSelectInlineError(selectEl, message) {
    var $select = $(selectEl);
    var $container = $select.closest('.card .content');
    var $error = $container.find('.multiselect-required-error').first();

    if (message) {
        if (!$error.length) {
            $container.append('<p class="multiselect-required-error" style="color:#c00;margin-top:4px"></p>');
            $error = $container.find('.multiselect-required-error').first();
        }
        $error.text(message);
    } else if ($error.length) {
        $error.remove();
    }
}

function setCkeditorInlineError(textareaEl, message) {
    var $textarea = $(textareaEl);
    var $container = $textarea.closest('.card .content');
    var $error = $container.find('.ckeditor-required-error').first();

    if (message) {
        if (!$error.length) {
            $container.append('<p class="ckeditor-required-error" style="color:#c00;margin-top:4px"></p>');
            $error = $container.find('.ckeditor-required-error').first();
        }
        $error.text(message);
    } else if ($error.length) {
        $error.remove();
    }
}

function selectChanged(select) {
    console.log("select changed: " + select.name);
    var val = $(select).val();
    var selectOptions = $(select).find("option").map(function () {
        return $(this).val();
    }).get();
    selectOptions.forEach(function(option) {
        if (!option) return;
        if (!/^[A-Za-z0-9_-]+$/.test(option)) return;
        var element = $();
        var parentCard = $(select).closest('.card, .content');
        var candidates = parentCard.find('.' + option + '_wrap');
        candidates.each(function() {
            if ($(this).find(select).length === 0) {
                element = element.add(this);
            }
        });
        if (element.length === 0) {
            parentCard.find('div[class$="_wrap"]').each(function() {
                var classList = this.className.split(/\s+/);
                for (var i = 0; i < classList.length; i++) {
                    if (classList[i].endsWith('_wrap')) {
                        var base = classList[i].slice(0, -5).toLowerCase();
                        if (base.indexOf(option.toLowerCase()) !== -1 || option.toLowerCase().indexOf(base) !== -1) {
                            if ($(this).find(select).length === 0) {
                                element = element.add(this);
                            }
                        }
                    }
                }
            });
        }
        if (!element || element.length === 0) return;
        if (option !== val) {
            element.addClass('visually-hidden');
            element.find('*').each(function () {
                if ($(this).is('input, select, textarea')) {
                    $(this).attr('required', false);
                    $(this).addClass('visually-hidden');
                    $(this).attr('disabled', true);
                }
            });
            clearValuesWithin(element);
        } else {
            element.removeClass('visually-hidden');
            element.find('*').each(function () {
                if ($(this).attr('name') && $(this).attr('name').indexOf('[]') === -1) {
                    lookupClass = '.' + $(this).attr('name') + '_wrap';
                } else {
                    lookupClass = '.card';
                }
                if ($(this).is('input, select, textarea')) {
                    var label = $(this).closest(lookupClass).find("label[for='" + $(this).attr('name') + "']");
                    if (label.find('small.required').length > 0) {
                        $(this).attr('required', true);
                    }
                }
                $(this).removeClass('visually-hidden');
                $(this).attr('disabled', false);
            });
        }
    });
}

function toggleFieldsetField(element, className, checkedAction, isInit) {
    wrap = $(element).closest('fieldset').find('.' + className + '_wrap');
    showField = $(element).hasClass('checked');
    if (isInit) {
        if (checkedAction === 'show') {
            showField = true;
        } else {
            showField = false;
        }
    } else {
        if (checkedAction === 'show') {
            showField = !showField;
        }
    }
    if (showField) {
        wrap.find('*').each(function () {
            if ($(this).is('input, select, textarea')) {
                var label = $(this).closest('.card').find("label[for='" + $(this).attr('name') + "']");
                if (label.find('small.required').length > 0) {
                    $(this).attr('required', true);
                }
            }
            $(this).removeClass('visually-hidden');
        });
    } else {
        wrap.find('*').each(function () {
            $(this).addClass('visually-hidden');
            $(this).removeAttr('required');
        });
        clearValuesWithin(wrap);
    }
}

function clearValuesWithin(element) {
    $(element).find("select").each(function () {
        $(this).prop('selectedIndex', 0);
    });
    $(element).find("input[type='checkbox'], input[type='radio']").each(function () {
        $(this).prop("checked", false);
    });
    $(element).find("label").each(function () {
        $(this).removeClass('checked');
        if ($(this).attr('onclick')) {
            $(this).trigger('click');
        }
    });
    $(element).find("input.datepicker").each(function () {
        $(this).val('');
        if (this._pikaday) {
            this._pikaday.clear();
        }
    });
    $(element).find("input:not([type='checkbox']):not([type='radio']):not([type='select']):not(input.datepicker)").each(function () {
        $(this).attr('value', '');
    });
}

function stripCostChars(input) {
    input.value = input.value.replace(/[$,]/g, '');
}

// Normalizes pasted content to plain ASCII text for datepicker inputs.
function cleanPastedText(text) {
    var mojibake = [
        ['\u00e2\u20ac\u201d', '\u2014'],  // em dash
        ['\u00e2\u20ac\u201c', '\u2013'],  // en dash
        ['\u00e2\u20ac\u2122', '\u2019'],  // right single quote
        ['\u00e2\u20ac\u02dc', '\u2018'],  // left single quote
        ['\u00e2\u20ac\u0153', '\u201c'],  // left double quote
        ['\u00e2\u20ac\x9d',   '\u201d'],  // right double quote
        ['\u00e2\u20ac\u00a6', '\u2026'],  // ellipsis
        ['\u00e2\u20ac\u00a2', '\u2022']   // bullet
    ];

    text = text || '';
    for (var i = 0; i < mojibake.length; i++) {
        text = text.split(mojibake[i][0]).join(mojibake[i][1]);
    }

    text = text
        .replace(/\u2014/g, '-')
        .replace(/\u2013/g, '-')
        .replace(/\u2018/g, "'")
        .replace(/\u2019/g, "'")
        .replace(/\u201c/g, '"')
        .replace(/\u201d/g, '"')
        .replace(/\u2026/g, '...')
        .replace(/\u00a0/g, ' ')
        .replace(/\u2022/g, '*');

    return text.replace(/[^\x20-\x7E\n\r\t]/g, '');
}

function addMultiple(groupName, buttonEl) {
    const $button = buttonEl ? $(buttonEl) : $();
    const originalLabel = $button.length ? $button.text() : '';
    const originalOpacity = $button.length ? $button.css('opacity') : '';
    if ($button.length) {
        $button
            .attr('aria-disabled', 'true')
            .css('pointer-events', 'none')
            .css('opacity', '0.7')
            .text('Adding...');
    }

    if (typeof CKEDITOR !== 'undefined') {
        for (const instanceName in CKEDITOR.instances) {
            if (Object.prototype.hasOwnProperty.call(CKEDITOR.instances, instanceName)) {
                CKEDITOR.instances[instanceName].updateElement();
            }
        }
    }

    // Preserve file input values
    const form = document.querySelector('#eventform');
    const fileInputs = form.querySelectorAll('input[type="file"]');
    const fileData = {};

    fileInputs.forEach(input => {
        if (input.files.length > 0) {
            fileData[input.name] = input.files;
        }
    });

    const payload = $('#eventform').serializeArray();
    payload.push({ name: 'group_name', value: groupName });

    $.ajax({
        url: addMultipleUrl, // Use the resolved URL
        method: 'POST',
        data: payload,
        success: function(response) {
            console.log('Server response:', response); // Debugging log
            if (!response || typeof response.html !== 'string') {
                console.error('Invalid response format:', response);
                return;
            }

            if (typeof CKEDITOR !== 'undefined') {
                for (const instanceName in CKEDITOR.instances) {
                    if (Object.prototype.hasOwnProperty.call(CKEDITOR.instances, instanceName)) {
                        CKEDITOR.instances[instanceName].destroy(true);
                    }
                }
            }

            $('#event-form-fields').html(response.html);
            initializeDynamicFormUi();

            // Reapply file input values
            setTimeout(() => {
                Object.keys(fileData).forEach(name => {
                    const input = form.querySelector(`input[name="${name}"]`);
                    if (input) {
                        const dataTransfer = new DataTransfer();
                        Array.from(fileData[name]).forEach(file => dataTransfer.items.add(file));
                        input.files = dataTransfer.files;
                    }
                });
            }, 100);

            if (typeof CKEDITOR !== 'undefined' && CKEDITOR.replaceAll) {
                CKEDITOR.replaceAll('ckeditor');
            }
        },
        error: function() {
            console.error('Unable to add another item for group:', groupName);
        },
        complete: function() {
            if ($button.length && document.body.contains($button[0])) {
                $button
                    .attr('aria-disabled', 'false')
                    .css('pointer-events', '')
                    .css('opacity', originalOpacity)
                    .text(originalLabel);
            }
        }
    });
}

function removeMultiple(groupName, buttonEl) {
    const $button = buttonEl ? $(buttonEl) : $();
    const originalLabel = $button.length ? $button.text() : '';
    const originalOpacity = $button.length ? $button.css('opacity') : '';
    const originalClass = $button.length ? ($button.attr('class') || '') : '';

    if ($button.length) {
        $button
            .attr('aria-disabled', 'true')
            .css('pointer-events', 'none')
            .css('opacity', '0.7');

        if ($button.is('i')) {
            $button.removeClass('fa-times').addClass('fa-spinner fa-spin');
        } else {
            $button.text('Removing...');
        }
    }

    if (typeof CKEDITOR !== 'undefined') {
        for (const instanceName in CKEDITOR.instances) {
            if (Object.prototype.hasOwnProperty.call(CKEDITOR.instances, instanceName)) {
                CKEDITOR.instances[instanceName].updateElement();
            }
        }
    }

    const payload = $('#eventform').serializeArray();
    payload.push({ name: 'group_name', value: groupName });

    $.ajax({
        url: removeMultipleUrl, // Use the resolved URL
        method: 'POST',
        data: payload,
        success: function(response) {
            if (!response || typeof response.html !== 'string') {
                return;
            }

            if (typeof CKEDITOR !== 'undefined') {
                for (const instanceName in CKEDITOR.instances) {
                    if (Object.prototype.hasOwnProperty.call(CKEDITOR.instances, instanceName)) {
                        CKEDITOR.instances[instanceName].destroy(true);
                    }
                }
            }

            $('#event-form-fields').html(response.html);
            initializeDynamicFormUi();

            if (typeof CKEDITOR !== 'undefined' && CKEDITOR.replaceAll) {
                CKEDITOR.replaceAll('ckeditor');
            }
        },
        error: function() {
            console.error('Unable to remove item for group:', groupName);
        },
        complete: function() {
            if ($button.length && document.body.contains($button[0])) {
                $button
                    .removeAttr('aria-disabled')
                    .css('pointer-events', '')
                    .css('opacity', originalOpacity);

                if ($button.is('i')) {
                    $button.attr('class', originalClass);
                } else {
                    $button.text(originalLabel);
                }
            }
        }
    });
}

function updateFieldsets(name, scope, displayPrefix) {
    displayPrefix = (displayPrefix !== undefined && displayPrefix !== null) ? String(displayPrefix) : '';
    var $context = scope ? $(scope) : $(document);

    var sets = $context.find('.' + name + '_fieldset.fieldset').not('.fieldset_template');
    var count = sets.length;
    var id = 1;

    sets.each(function () {
        var $this = $(this);
        var isMultiple = $this.data('fieldset-type') === 'multiple';
        var $legend = $this.find('> .card > .content > legend');
        var displayNum = displayPrefix ? displayPrefix + '-' + id : String(id);
        var childPrefix = isMultiple ? displayNum : displayPrefix;

        $this.attr('fieldset-id', id);

        if (isMultiple) {
            $legend.find('> span.fieldset_number').text(displayNum);
            if (count < 2) {
                $legend.find('> .fa-delete').addClass('visually-hidden');
            } else {
                $legend.find('> .fa-delete').removeClass('visually-hidden');
            }
        }

        // Recursively update nested multiple fieldsets, scoped to this card.
        // Tag each nested fieldset element with the outer row index (data-parent-row)
        // so that its inputs get row-aware key names like
        //   scheduleDetails_timeDescription_fieldset_1::timeDescription_time[]
        // instead of the ambiguous
        //   scheduleDetails_timeDescription_fieldset::timeDescription_time[]
        var thisEl = this;
        $this.find('[data-fieldset-name]').filter(function () {
            return $(this).closest('.fieldset').not('.fieldset_template')[0] === thisEl;
        }).each(function () {
            var innerName = $(this).data('fieldset-name');
            // Mark inner fieldset elements before recursing so input renaming below picks up the row
            $this.find('.' + innerName + '_fieldset.fieldset').not('.fieldset_template').each(function () {
                $(this).attr('data-parent-row', id);
            });
            updateFieldsets(innerName, thisEl, childPrefix);
        });

        // Update input names within this card, but skip anything inside a
        // nested fieldset_template (those are cloning templates — modifying
        // their ids/names corrupts future duplications from that scope).
        $this.find('.card input, .card select, .card textarea').filter(function () {
            return $(this).closest('.fieldset_template').length === 0;
        }).each(function () {
            $(this).removeAttr('id');
            var inputName = $(this).attr('name');
            if (inputName && !inputName.endsWith('[]')) {
                var $parentFieldset = $(this).closest('.card').parent('fieldset');
                var classAttr = $parentFieldset.attr('class');
                var fieldClass = classAttr ? classAttr.split(' ')[0] : '';
                var parentRow = $parentFieldset.attr('data-parent-row');
                var prefix = parentRow ? fieldClass + '_' + parentRow : fieldClass;
                $(this).attr('name', prefix + '::' + inputName + '[]');
                var inputId = prefix + '::' + inputName + '[]';
                $(this).closest('.card').find("label[for='" + inputName + "']").attr('for', inputId);
            }
        });

        id++;
    });
}

function initializeDynamicFormUi() {
    $("select[onchange*='selectChanged']").each(function() {
        selectChanged(this);
    });

    $('label.checkbox').each(function () {
        var onclickAction = $(this).attr('onclick');
        if (onclickAction) {
            var onclickStr = onclickAction.toString();

            if ($(this).hasClass('checked')) {
                var match = onclickStr.match(/toggleFieldsetField\(([^)]*)\)/);
                if (match) {
                    var args = match[1].split(',').map(function(arg) {
                        arg = arg.trim();
                        if (arg.startsWith("'") && arg.endsWith("'")) {
                            return arg.slice(1, -1);
                        } else if (arg.startsWith('"') && arg.endsWith('"')) {
                            return arg.slice(1, -1);
                        } else if (arg === "this") {
                            return this;
                        } else {
                            return arg;
                        }
                    }.bind(this));
                    toggleFieldsetField.apply(null, [...args, true]);
                }
            }
        }
    });

    $('.datepicker').each(function () {
        var el = this;
        if (this._pikaday) {
            this._pikaday.destroy();
        }
        this._pikaday = new Pikaday({
            field: this,
            format: 'MMMM Do YYYY, h:mm a',
            showTime: true,
            onSelect: function () {
                syncDates(el);
            }
        });
    });

    $('.fieldset').not('.fieldset_template').filter(function () {
        return $(this).parent().closest('.fieldset').not('.fieldset_template').length === 0;
    }).each(function () {
        var fieldsetName = getFieldsetName(this);
        if (fieldsetName) {
            updateFieldsets(fieldsetName);
        }
    });
}

// When "All-day event?" is checked, set start to midnight and end to end of day.
function setAllDayTime(target) {
    var $target = $(target);
    var targetIsCheckbox = $target.is('input[type="checkbox"]');
    var $checkbox = targetIsCheckbox ? $target : $target.find('input[type="checkbox"]');
    if (!$checkbox.length) return;

    var $card = $checkbox.closest('.card');
    var $startInput = $card.find('.date__eventStart_wrap input.datepicker');
    var $endInput   = $card.find('.date__eventEnd_wrap input.datepicker');
    var format = 'MMMM Do YYYY, h:mm a';

    function zeroTime($input) {
        var val = $input.val();
        if (!val) return;
        var m = moment(val, format);
        if (!m.isValid()) return;
        m.startOf('day');  // sets time to 00:00:00
        $input.val(m.format(format));
        if ($input[0] && $input[0]._pikaday) {
            $input[0]._pikaday.setDate(m.toDate(), true);
        }
    }

    function endTime($input) {
        var val = $input.val();
        if (!val) return;
        var m = moment(val, format);
        if (!m.isValid()) return;
        m.endOf('day');  // sets time to 23:59:59
        $input.val(m.format(format));
        if ($input[0] && $input[0]._pikaday) {
            $input[0]._pikaday.setDate(m.toDate(), true);
        }
    }

    zeroTime($startInput);
    endTime($endInput);
}

// Ensures the event end date/time is never before the event start date/time.
// If end < start, snaps end to equal start.
function syncDates(element) {
    var $card = $(element).closest('.card');
    var $startInput = $card.find('.date__eventStart_wrap input.datepicker');
    var $endInput = $card.find('.date__eventEnd_wrap input.datepicker');
    var format = 'MMMM Do YYYY, h:mm a';

    var startVal = $startInput.val();
    var endVal = $endInput.val();

    // If start is set but end is empty, copy start to end
    // if (startVal && !endVal) {
    //     $endInput.val(startVal);
    //     if ($endInput[0] && $endInput[0]._pikaday) {
    //         $endInput[0]._pikaday.setDate(moment(startVal, format).toDate(), true);
    //     }
    //     return;
    // }

    if (!startVal || !endVal) return;

    var startMoment = moment(startVal, format);
    var endMoment = moment(endVal, format);

    if (!startMoment.isValid() || !endMoment.isValid()) return;

    // If end is before start, snap end to match start
    if (endMoment.isBefore(startMoment)) {
        $endInput.val(startMoment.format(format));
        if ($endInput[0] && $endInput[0]._pikaday) {
            $endInput[0]._pikaday.setDate(startMoment.toDate(), true);
        }
    }
}

function getFieldsetName(element) {
    var classAttr = $(element).attr('class');
    var classes = classAttr ? classAttr.split(/\s+/) : [];
    var fieldsetName = null;
    for (var i = 0; i < classes.length; i++) {
        var match = classes[i].match(/^(.+)_fieldset$/);
        if (match && match[1]) {
            fieldsetName = match[1];
            break;
        }
    }
    return fieldsetName;
}

// Global counter for unique CKEditor textarea IDs across all dynamically created fieldsets.
var _ckIdCounter = 0;

function validateRequiredRichFields($form) {
    var firstInvalidElement = null;
    var firstInvalidEditor = null;

    // Keep textarea values in sync before any validity checks.
    if (typeof CKEDITOR !== 'undefined') {
        for (var editorName in CKEDITOR.instances) {
            if (Object.prototype.hasOwnProperty.call(CKEDITOR.instances, editorName)) {
                CKEDITOR.instances[editorName].updateElement();
            }
        }
    }

    // Required multi-selects rendered manually in Jinja should still participate
    // in native HTML validity checks.
    $form.find('select[multiple]').each(function () {
        this.setCustomValidity('');
        setMultiSelectInlineError(this, '');
        if (!this.hasAttribute('required') || this.disabled) return;
        if ($(this).val() && $(this).val().length > 0) return;
        var msg = 'Please select at least one option.';
        this.setCustomValidity(msg);
        setMultiSelectInlineError(this, msg);
        if (!firstInvalidElement) firstInvalidElement = this;
    });

    // Required CKEditor fields are validated from editor content.
    if (typeof CKEDITOR !== 'undefined') {
        for (var instanceName in CKEDITOR.instances) {
            if (!Object.prototype.hasOwnProperty.call(CKEDITOR.instances, instanceName)) continue;
            var instance = CKEDITOR.instances[instanceName];
            var textarea = instance.element && instance.element.$;
            if (!textarea) continue;

            textarea.setCustomValidity('');
            setCkeditorInlineError(textarea, '');
            var isRequiredEditor = textarea.hasAttribute('required') ||
                textarea.getAttribute('data-required-ckeditor') === '1' ||
                $(textarea).closest('.card .content').find('legend small.required, label small.required').length > 0;
            if (!isRequiredEditor || textarea.disabled) continue;

            var html = instance.getData();
            var text = html.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim();
            if (text) continue;

            var ckMsg = 'This field is required.';
            textarea.setCustomValidity(ckMsg);
            setCkeditorInlineError(textarea, ckMsg);
            if (!firstInvalidElement) firstInvalidElement = textarea;
            if (!firstInvalidEditor) firstInvalidEditor = instance;
        }
    }

    if (!firstInvalidElement) return true;

    if (firstInvalidEditor) {
        firstInvalidEditor.focus();
        var editorFieldset = firstInvalidEditor.element && firstInvalidEditor.element.$
            ? $(firstInvalidEditor.element.$).closest('.card .content')[0]
            : null;
        if (editorFieldset) {
            editorFieldset.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    } else {
        firstInvalidElement.focus();
        if (typeof firstInvalidElement.reportValidity === 'function') {
            firstInvalidElement.reportValidity();
        }
    }

    return false;
}

function openImagePreviewModal(imageUrl, imageAlt) {
    var $modal = $('#image-preview-modal');
    var $image = $('#image-preview-modal-image');
    if (!$modal.length || !$image.length) return;

    $image.attr('src', imageUrl || '');
    $image.attr('alt', imageAlt || 'Image preview');
    $modal.removeClass('visually-hidden').attr('aria-hidden', 'false');
}

function closeImagePreviewModal() {
    var $modal = $('#image-preview-modal');
    var $image = $('#image-preview-modal-image');
    if (!$modal.length) return;

    $modal.addClass('visually-hidden').attr('aria-hidden', 'true');
    if ($image.length) {
        $image.attr('src', '');
    }
}

function renderSelectedFilePreview(fileInput) {
    var file = fileInput && fileInput.files && fileInput.files[0];
    if (!file) return;
    if (!file.type || file.type.indexOf('image/') !== 0) return;

    var $input = $(fileInput);
    var $container = $input.closest('.card .content');
    var labelText = $container.find("label[for='" + ($input.attr('id') || '') + "']").text().trim() || 'Image preview';

    var $previewInline = $container.find('.image-preview-inline').first();
    if (!$previewInline.length) {
        $previewInline = $('<div class="image-preview-inline"></div>');
        $previewInline.insertAfter($input.siblings("input[type='hidden'][name$='_path']").last());
    }

    var $trigger = $previewInline.find('.image-preview-trigger').first();
    if (!$trigger.length) {
        $trigger = $('<a href="#" class="image-preview-trigger" data-preview-url="" data-preview-alt=""></a>');
        $previewInline.append($trigger);
    }

    var $img = $trigger.find('.image-preview-thumb').first();
    if (!$img.length) {
        $img = $('<img class="image-preview-thumb" alt="" />');
        $trigger.append($img);
    }

    var objectUrl = URL.createObjectURL(file);
    var prevObjectUrl = $trigger.data('objectUrl');
    if (prevObjectUrl) {
        URL.revokeObjectURL(prevObjectUrl);
    }

    $trigger.data('objectUrl', objectUrl);
    $trigger.attr('data-preview-url', objectUrl);
    $trigger.attr('data-preview-alt', labelText);

    $img.attr('src', objectUrl);
    $img.attr('alt', labelText);

    var $small = $previewInline.find('small.small-link').first();
    if (!$small.length) {
        $small = $('<small class="small-link"></small>');
        $previewInline.append($small);
    }
    $small.text(file.name);
}

$(document).ready(function () {
    initializeDynamicFormUi();

    // Sanitize pasted content for all text inputs and textareas in the event form.
    $(document).on('paste', '#eventform input[type="text"], #eventform textarea', function (e) {
        e.preventDefault();
        var clipboard = e.originalEvent.clipboardData || window.clipboardData;
        var pastedText = clipboard ? clipboard.getData('text') : '';
        var cleaned = cleanPastedText(pastedText);
        var el = e.target;
        var start = el.selectionStart || 0;
        var end = el.selectionEnd || 0;
        var current = el.value || '';

        el.value = current.substring(0, start) + cleaned + current.substring(end);
        el.selectionStart = el.selectionEnd = start + cleaned.length;

        $(el).trigger('input');
    });

    $(document).on('click', '.image-preview-trigger', function (e) {
        e.preventDefault();
        var imageUrl = $(this).data('preview-url');
        var imageAlt = $(this).data('preview-alt') || 'Image preview';
        openImagePreviewModal(imageUrl, imageAlt);
    });

    $(document).on('click', '[data-image-preview-close]', function () {
        closeImagePreviewModal();
    });

    $(document).on('keydown', function (e) {
        if (e.key === 'Escape') {
            closeImagePreviewModal();
        }
    });

    $(document).on('change', '#eventform input[type="file"]', function () {
        renderSelectedFilePreview(this);
    });

    $('#eventform').on('submit', function (e) {
        var $form = $(this);
        var $submitBtn = $form.find('#event-submit-btn');

        if ($form.data('isSubmitting')) {
            e.preventDefault();
            return;
        }

        if (!validateRequiredRichFields($form)) {
            e.preventDefault();
            return;
        }

        $form.data('isSubmitting', true);
        if ($submitBtn.length) {
            $submitBtn
                .addClass('is-submitting')
                .attr('aria-disabled', 'true')
                .css('pointer-events', 'none');
        }
    });

    // Clear multiselect inline errors as soon as selection becomes valid.
    $(document).on('change', '#eventform select[multiple]', function () {
        this.setCustomValidity('');
        if (!this.hasAttribute('required') || this.disabled) {
            setMultiSelectInlineError(this, '');
            return;
        }
        if ($(this).val() && $(this).val().length > 0) {
            setMultiSelectInlineError(this, '');
        }
    });

    // Clear custom validity for required editors when users type.
    if (typeof CKEDITOR !== 'undefined') {
        CKEDITOR.on('instanceReady', function (ev) {
            // CKEditor handles clipboard input internally, so sanitize at the editor paste event.
            ev.editor.on('paste', function (pasteEvent) {
                pasteEvent.data.dataValue = cleanPastedText(
                    pasteEvent.data.dataValue
                        .replace(/<[^>]+>/g, ' ')
                        .replace(/&amp;/g, '&')
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>')
                        .replace(/&nbsp;/g, ' ')
                );
            });

            ev.editor.on('change', function () {
                if (ev.editor.element && ev.editor.element.$) {
                    ev.editor.element.$.setCustomValidity('');
                    setCkeditorInlineError(ev.editor.element.$, '');
                }
            });
        });
    }
});