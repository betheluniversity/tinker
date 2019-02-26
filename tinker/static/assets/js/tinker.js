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

function searchCookie(prevInputs, type, groups) {
    let inputs = prevInputs;
    if (Cookies.get(type + "-search-cookie") != null) {
        inputs = Cookies.get(type + "-search-cookie");
    }
    Cookies.set(type + "-search-cookie", inputs, { expires: 1, path: '/' });

    let viewList = []
    if (type === "event") {
        viewList = ['My Events', 'All Events', 'Other Events', 'User Events'];
        $("#search-box").empty();
        $("#search-box").append("<label for=\"event-title\">Event Title:</label>\n" +
            "<input id=\"event-title\" type=\"text\" name=\"event-title\"class=\"input-field\" value=\"" + inputs.split("-")[0] + "\"><br/>\n" +
            "<label for=\"start-date\">Date Range:<br />\n" +
            "<span>\n" +
            "<input id=\"start-date\" class=\"datepicker input-field date-range\" size=\"11\" value=\"" + inputs.split("-")[1] +" \">\n" +
            "<input id=\"end-date\" class=\"datepicker input-field date-range\" size=\"11\" value=\"" + inputs.split("-")[2] + " \">\n" +
            "</span>\n" +
            "</label>")
    } else if (type === "e-announcement") {
        viewList = ['My E-Announcements', 'All E-Announcements', 'Other E-Announcements', 'User E-Announcements'];
        $("#search-box").empty();
        $("#search-box").append("<label for=\"e-annz-title\">E-Announcement Title:</label>\n" +
            "<input id=\"e-annz-title\" type=\"text\" name=\"E-Annz-Title\" class=\"input-field\" value=\"" + inputs.split("-")[0] + "\">\n" +
            "<label for=\"e-annz-date\">E-Announcement Date</label>\n" +
            "<input id=\"e-annz-date\" class='datepicker input-field date-range' size='11' value=\"" + inputs.split("-")[1] + "\">")
    }

    let lastInput = inputs.split("-").length - 1;
    let selected = 0;
    if (!inputs.split("-")[lastInput]) {
        selected = $("#school-selector").children("option:selected").attr("value");
    }
    $("#school-selector").empty();
    if (groups.includes('Tinker Events - CAS') || groups.includes('Event Approver') || groups.includes('Tinker E-Announcements - CAS') || groups.includes('E-Announcement Approver')) {
        for (let i = 0; i < viewList.length - 1; i ++) {
            if (inputs.split("-")[lastInput] - 1 == i || selected - 1 == i) {
                $("#school-selector").append("<option value=\""+ (i + 1) +"\" selected='selected'>" + viewList[i] + "</option>");
            } else {
                $("#school-selector").append("<option value=\""+ (i + 1) +"\">" + viewList[i] + "</option>");
            }
        }
    } else {
        if (type === "event") {
            $("#school-selector").append("<option value=\""+ 1 +"\" selected='selected'>" + viewList[lastInput] + "</option>");
        } else {
            $("#school-selector").append("<option value=\""+ 1 +"\" selected='selected'>" + viewList[lastInput + 1] + "</option>");
        }
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
        var picker = new Pikaday(starting_values);
    });

    // TODO MAKE ALL THESE BELOW INTO ONE METHOD

    $("#event-title").change(function(e) {
        var currentValue = $(this).val();
        let newInputs = (currentValue + "-" + inputs.split("-")[1] + "-" + inputs.split("-")[2] + "-" + inputs.split("-")[3]);
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#start-date").change(function(e) {
        var currentValue = $(this).val();
        let newInputs = (inputs.split("-")[0] + "-" + currentValue + "-" + inputs.split("-")[2] + "-" + inputs.split("-")[3]);
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#end-date").change(function(e) {
        var currentValue = $(this).val();
        let newInputs = (inputs.split("-")[0] + "-" + inputs.split("-")[1] + "-" + currentValue + "-" + inputs.split("-")[3]);
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#e-annz-title").change(function(e) {
        var currentValue = $(this).val();
        let newInputs = (currentValue + "-" + inputs.split("-")[1] + "-" + inputs.split("-")[2]);
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#e-annz-date").change(function(e) {
        var currentValue = $(this).val();
        let newInputs = (inputs.split("-")[0] + "-" + currentValue + "-" + inputs.split("-")[2]);
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#school-selector").change(function() {
        let selected = $("#school-selector").children("option:selected").attr("value");
        let newInputs = ""
        for (let i = 0; i < inputs.split("-").length - 1; i ++) {
            newInputs += inputs.split("-")[i] + "-";
        }
        newInputs += "" + selected;
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });
}