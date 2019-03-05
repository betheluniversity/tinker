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

        $("#event-title").val(inputs.split("-")[0]);
        $("#start-date").val(inputs.split("-")[1]);
        $("#end-date").val(inputs.split("-")[2]);
    } else if (type === "e-announcement") {
        viewList = ['My E-Announcements', 'All E-Announcements', 'Other E-Announcements', 'User E-Announcements'];

        $("#e-annz-title").val(inputs.split("-")[0]);
        $("#e-annz-date").val(inputs.split("-")[1]);
    }

    let lastInput = inputs.split("-").length - 1;
    let selected = 0;
    if (!inputs.split("-")[lastInput]) {
        selected = $("#school-selector").children("option:selected").attr("value");
    }
    if ((type === "event" && (groups.includes('Tinker Events - CAS') || groups.includes('Event Approver'))) || (type === "e-announcement" && (groups.includes('Tinker E-Announcements - CAS') || groups.includes('E-Announcement Approver')))) {
        for (let i = 0; i < viewList.length - 1; i ++) {
            let id = "#" + (i + 1);
            $("#school-selector").children().removeAttr("selected");
            if (inputs.split("-")[lastInput] - 1 == i || selected - 1 == i) {
                $(id).prop("selected", true);
                break;
            }
        }
    }

    $("#event-title").change(function(e) {
        let currentValue = $(this).val();
        let newInputs = (currentValue + "-" + inputs.split("-")[1] + "-" + inputs.split("-")[2] + "-" + inputs.split("-")[3]);
        inputs = newInputs;
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#start-date").change(function(e) {
        let currentValue = $(this).val();
        let newInputs = (inputs.split("-")[0] + "-" + currentValue + "-" + inputs.split("-")[2] + "-" + inputs.split("-")[3]);
        inputs = newInputs;
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#end-date").change(function(e) {
        let currentValue = $(this).val();
        let newInputs = (inputs.split("-")[0] + "-" + inputs.split("-")[1] + "-" + currentValue + "-" + inputs.split("-")[3]);
        inputs = newInputs;
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#e-annz-title").change(function(e) {
        let currentValue = $(this).val();
        let newInputs = (currentValue + "-" + inputs.split("-")[1] + "-" + inputs.split("-")[2]);
        inputs = newInputs;
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#e-annz-date").change(function(e) {
        let currentValue = $(this).val();
        let newInputs = (inputs.split("-")[0] + "-" + currentValue + "-" + inputs.split("-")[2]);
        inputs = newInputs;
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });

    $("#school-selector").change(function() {
        let selected = $("#school-selector").children("option:selected").attr("value");
        let newInputs = "";
        for (let i = 0; i < inputs.split("-").length - 1; i ++) {
            newInputs += inputs.split("-")[i] + "-";
        }
        newInputs += "" + selected;
        inputs = newInputs;
        Cookies.set(type + "-search-cookie", newInputs, { expires: 1, path: '/' })
    });
}
