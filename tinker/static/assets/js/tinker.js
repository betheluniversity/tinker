// General File for Tinker's JavaScript

$(document).ready(function () {
    $("#search-filters").click(function () {
        if($(this).hasClass("show")) {
            $("#additional-search-params").slideUp();
            $(this).removeClass("show");
            $(this).addClass("no-show");
            $(this).text("+ More Search Filters")
        }else{
            $("#additional-search-params").slideDown();
            $(this).removeClass("no-show");
            $(this).addClass("show");
            $(this).text("- Less Search Filters")
        }
    });
});

function searchCookie(prevInputs, type) {
    let inputs = prevInputs;
    if (Cookies.get(type + "-search-cookie") != null) {
        inputs = Cookies.get(type + "-search-cookie");
    }
    Cookies.set(type + "-search-cookie", inputs, { expires: 365, path: '/' });

    if (type === "event") {
        $("#search-box").empty();
        $("#search-box").append("<label for=\"event-title\">Event Title:</label>\n" +
            "<input id=\"event-title\" type=\"text\" name=\"event-title\"class=\"input-field\" value=\"" + inputs.split("-")[0] + "\"><br/>\n" +
            "<label for=\"start-date\">Date Range:<br />\n" +
            "<span>\n" +
            "<input id=\"start-date\" class=\"datepicker input-field date-range\" size=\"11\" value=\"" + inputs.split("-")[1] +" \">\n" +
            "<input id=\"end-date\" class=\"datepicker input-field date-range\" size=\"11\" value=\"" + inputs.split("-")[2] + "\">\n" +
            "</span>\n" +
            "</label>")
    } else if (type === "e-announcement") {
        $("#search-box").empty();
        $("#search-box").append("<label for=\"e-annz-title\">E-Announcement Title:</label>\n" +
            "<input id=\"e-annz-title\" type=\"text\" name=\"E-Annz-Title\" class=\"input-field\" value=\"" + inputs.split("-")[0] + "\">\n" +
            "<label for=\"e-annz-date\">E-Announcement Date</label>\n" +
            "<input id=\"e-annz-date\" class='datepicker input-field date-range' size='11' value=\"" + inputs.split("-")[1] + "\">")
    }
    $('.datepicker').each(function () {
        var current_element = $(this);
        var starting_values = {
            field: this,
            format: 'MM DD YYYY',
            minDate: new Date('2000-01-01'),
            maxDate: new Date('2040-12-31'),
            yearRange: [2000, 2040],
            disableDayFn: function (date) {
                var start_populated = $("#start-date").val();
                var end_populated = $("#end-date").val();
                if (start_populated == "" && end_populated == "") {
                    return null;
                } else if (start_populated != "" && current_element.attr('id') == 'end-date') {
                    if (new Date(start_populated) >= date) {
                        return date;
                    }
                } else if (end_populated != "" && current_element.attr('id') == 'start-date') {
                    if (new Date(end_populated) <= date) {
                        return date;
                    }
                }
            }
        };
        // if ($(this).attr('id') == 'start-date'){
        //     starting_values['defaultDate'] = new Date();
        //     starting_values['setDefaultDate'] = false;
        // }
        var picker = new Pikaday(starting_values);
    });

    var previousValue = $("#event-title").val();
    $("#event-title").change(function(e) {
        var currentValue = $(this).val();
        if(currentValue != previousValue) {
            previousValue = currentValue;
            let newInputs = (currentValue + "-" + inputs.split("-")[1] + "-" + inputs.split("-")[2]);
            Cookies.set(type + "-search-cookie", newInputs, { expires: 365, path: '/' })
        }
    });
    var previousValue = $("#start-date").val();
    $("#start-date").change(function(e) {
        var currentValue = $(this).val();
        if(currentValue != previousValue) {
            previousValue = currentValue;
            let newInputs = (inputs.split("-")[0] + "-" + currentValue + "-" + inputs.split("-")[2]);
            Cookies.set(type + "-search-cookie", newInputs, { expires: 365, path: '/' })
        }
    });
    var previousValue = $("#end-date").val();
    $("#end-date").change(function(e) {
        var currentValue = $(this).val();
        if(currentValue != previousValue) {
            previousValue = currentValue;
            let newInputs = (inputs.split("-")[0] + "-" + inputs.split("-")[1] + "-" + currentValue);
            Cookies.set(type + "-search-cookie", newInputs, { expires: 365, path: '/' })
        }
    });
    var previousValue = $("#e-annz-title").val();
    $("#e-annz-title").change(function(e) {
        var currentValue = $(this).val();
        if(currentValue != previousValue) {
            previousValue = currentValue;
            let newInputs = (currentValue + "-" + inputs.split("-")[1]);
            Cookies.set(type + "-search-cookie", newInputs, { expires: 365, path: '/' })
        }
    });
    var previousValue = $("#e-annz-date").val();
    $("#e-annz-date").change(function(e) {
        var currentValue = $(this).val();
        if(currentValue != previousValue) {
            previousValue = currentValue;
            let newInputs = (inputs.split("-")[0] + "-" + currentValue);
            Cookies.set(type + "-search-cookie", newInputs, { expires: 365, path: '/' })
        }
    });
}