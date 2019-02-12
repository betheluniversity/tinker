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

function pagination(type) {
    var numberOfItems = $(" #loop .items-to-paginate").length;
    if (numberOfItems > 10) {
        var limitPerPage = 10;
        if (type == 'e-announcement') {
            if (Cookies.get('e-announcement-cookie') != null) {
                limitPerPage = Cookies.get('e-announcement-cookie');
            } else {
                Cookies.set('e-announcement-cookie', limitPerPage, { expires: 30, path: '/' });
            }
        } else if (type == 'event') {
            if (Cookies.get('event-cookie') != null) {
                limitPerPage = Cookies.get('event-cookie');
            } else {
                Cookies.set('event-cookie', limitPerPage, { expires: 30, path: '/' });
            }
        }

        var limitList = [10, 25, 50, numberOfItems]

        for (var i = 0; i < limitList.length; i ++) {
            if (limitList[i] == limitPerPage) {
                if (limitList[i] == numberOfItems) {
                     $("#selected-option").append("<option value=\" " + limitList[i] + " \" selected='selected'>All</option>");
                } else {
                    $("#selected-option").append("<option value=\" " + limitList[i] + " \" selected='selected'>" + limitList[i] + "</option>");
                }
            } else {
                if (limitList[i] == numberOfItems) {
                    $("#selected-option").append("<option value=\" " + limitList[i] + " \">All</option>");
                } else {
                    $("#selected-option").append("<option value=\" " + limitList[i] + " \">" + limitList[i] + "</option>");
                }
            }
        }

        $("#selected-option").change(function() {
            limitPerPage = $("#selected-option").children("option:selected").attr("value");
            if (type == 'e-announcement') {
                Cookies.set('e-announcement-cookie', limitPerPage, { expires: 30, path: '/' });
            } else if (type == 'event') {
                Cookies.set('event-cookie', limitPerPage, { expires: 30, path: '/' });
            }

            $(".pagination").children("li.temp-button").remove();

            var totalPages = Math.ceil(numberOfItems / limitPerPage);

            createButtons(totalPages, limitPerPage);

            // When a new limit is selected, we reset the current page to one, since if we have 10 pages, and then
            // we changed to only having one page, we can't keep whatever page we were previously on (if it was greater
            // than 1) so we instead just set it to 1.
            var currentPage = 1;

            var grandTotal = limitPerPage * currentPage;

            for (var i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
                $("#loop .items-to-paginate:eq(" + i + ")").show();
            }

            switchPageClick(limitPerPage, totalPage, "");

            nextOrPreviousPage(totalPages, limitPerPage, "next-page");

            goToPage(limitPerPage, totalPages);

        });

        var totalPages = Math.ceil(numberOfItems / limitPerPage);

        createButtons(totalPages, limitPerPage);

        switchPageClick(limitPerPage, totalPages, "");

        nextOrPreviousPage(totalPages, limitPerPage, "next-page");

        nextOrPreviousPage(totalPages, limitPerPage, "previous-page");

        goToPage(limitPerPage, totalPages);
    }
}

// TODO Maybe instead of this, just have the next/prev buttons call the switch page method with the new current page value
function nextOrPreviousPage(totalPages, limitPerPage, type) {
    $("#" + type + " ").on("click", function () {
        var currentPage = $(".pagination li.active").index();
        // TODO THIS IS BAD CODE BETWEEN THE LINES ----------------------------
        if (type === "next-page") {
            var x = (document.getElementsByClassName("temp-button")[currentPage]).id;
        } else {
            var x = (document.getElementsByClassName("temp-button")[currentPage - 2]).id;
        }
        var interval = 1;
        if ((x.split("-")[0]) === "dot") {
            interval = 2;
        }
        // TODO THIS IS BAD CODE BETWEEN THE LINES ----------------------------
        if (type === "next-page") {
            if (currentPage === totalPages + 3) {
                return false;
            } else {
                currentPage++;
            }
        } else if (type === "previous-page") {
            if (currentPage === 1) {
                return false;
            } else {
                currentPage--;
            }
        }
        $(".pagination li").removeClass("active");
        $("#loop .items-to-paginate").hide();

        var grandTotal = limitPerPage * currentPage;

        if ((x.split('-')[0]) !== "dot") {
            if (currentPage < 2) {
                for (var i = grandTotal - limitPerPage; i < grandTotal; i++) {
                    $("#loop .items-to-paginate:eq(" + i + ")").show();
                }
            } else if (currentPage > 2 && currentPage < 6) {
                for (var i = grandTotal - limitPerPage - 10; i < grandTotal - 10; i++) {
                    $("#loop .items-to-paginate:eq(" + i + ")").show();
                }
            } else if (currentPage > 6 && currentPage < 15) {
                for (var i = grandTotal - limitPerPage - 20; i < grandTotal - 20; i++) {
                    $("#loop .items-to-paginate:eq(" + i + ")").show();
                }
            } else {
                for (var i = grandTotal - limitPerPage - 30; i < grandTotal - 30; i++) {
                    $("#loop .items-to-paginate:eq(" + i + ")").show();
                }
            }
        }

        $(".pagination li.current-page:eq(" + (currentPage - 1) + ")").addClass("active");

        ShowHideButtons(currentPage, totalPages);

    });
}

// This method changes the page when you input a page number and click "Go"
function goToPage(limitPerPage, totalPages) {
    $("button#go-to-button").on("click", function() {
        var page = document.getElementById("go-to-input");
        var value = Math.floor(page.value);
        if (value > 0 && value < totalPages + 1) {
            $(".pagination li").removeClass("active");
            var currentPage = value;
            if (currentPage < 2) {
                currentPage = currentPage - 1;
            } else if (currentPage == totalPages) {
                currentPage = currentPage + 2;
            } else if (currentPage >= 5) {
                currentPage = currentPage + 1;
            }
            $(".pagination li.current-page:eq(" + (currentPage) + ")").addClass("active");
            switchPages(limitPerPage, totalPages, Math.floor(page.value));
            page.value = "";
        } else {
            // TODO MAYBE THROW AN ERROR
            return;
        }
    });
}

// This method switches the page when you click on a button
function switchPageClick(limitPerPage, totalPages, newCurrentPage) {
    $(".pagination li.current-page").on("click", function() {
        if ($(this).hasClass("active")) {
            return false;
        } else {
            var currentPage = $(this).text();
            $(".pagination li").removeClass("active");
            $(this).addClass("active");
            switchPages(limitPerPage, totalPages, currentPage)
        }
    });
}

// This method hands off the current page to the ShowHideButtons function when a new button is either clicked or inputted
function switchPages(limitPerPage, totalPages, currentPage) {

    $("#loop .items-to-paginate").hide();
    var grandTotal = limitPerPage * currentPage;

    for (var i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
        $("#loop .items-to-paginate:eq(" + i + ")").show();
    }
    currentPage = parseInt(currentPage);
    if (currentPage < 2) {
        currentPage = currentPage;
    } else if (currentPage >= 2 && currentPage < 5) {
        currentPage = currentPage + 1;
    } else if (currentPage >= 5 && currentPage < totalPages - 2) {
        currentPage = currentPage + 2;
    } else {
        currentPage = currentPage + 3;
    }
    ShowHideButtons(currentPage, totalPages);
}

// This method makes the correct buttons show when you select a new button
function ShowHideButtons(currentPage, totalPages) {
    var x = (document.getElementsByClassName("temp-button")[currentPage - 1]).id;

    if ((x.split('-')[1]) == 1 || currentPage < 5) {
        for (var i = 1; i < totalPages; i++) {
            display([i.toString()],[]);
            if ((i > 0) && (i < 5)) {
                display([], [i.toString()]);
            }
        }
        display(["dot-1", "dot-3"], ["dot-2"]);
    } else if ((x.split('-')[1]) == 4 || currentPage > totalPages - 1) {
        for (var i = 2; i < totalPages; i++) {
            display([i.toString()],[]);
            if ((i > totalPages - 4)) {
                display([], [i.toString()]);
            }
        }
        display(["dot-1", "dot-3"], ["dot-2"]);
    } else {
        for (var i = 2; i < totalPages; i++) {
            display([i.toString()],[]);
            if ((i > (parseInt(x) - 2)) && (i < (parseInt(x) + 2))) {
                display([], [i.toString()]);
            }
        }
        display(["dot-2"], ["dot-1", "dot-3"]);
    }
}

// This method takes a list of html elements that will either be displayed as none or inline,
// iterates through the lists, and sets them to their desired display type
function display(none, inline) {
    if (none.length !== 0) {
        for (var i = 0; i < none.length; i++) {
            document.getElementById(none[i].toString()).style.display = "none";
        }
    }
    if (inline.length !== 0) {
        for (var i = 0; i < inline.length; i ++) {
            document.getElementById(inline[i].toString()).style.display = "inline";
        }
    }
}

// This method creates all the initial buttons for pagination, along with the dots if
function createButtons(totalPages, limitPerPage) {
    $(" #loop .items-to-paginate:gt(" + (limitPerPage - 1) + ")").hide();

    $(".pagination").append("<li id='1' class='current-page active temp-button'><a href='javascript:void(0)'>" + 1 + "</a></li>");
    $(".pagination").append("<li id='dot-1' style='display:none;' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");

    for (var i = 2; i <= totalPages; i++) {
        if (i > 4 && i < (totalPages - 3)) {
            if (i > 4 && i < 6 && totalPages > 6) {
                $(".pagination").append("<li id='dot-2' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");
            }
            $(".pagination").append("<li id='"+ i +"' style='display:none;' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
        } else if (i < 5) {
            $(".pagination").append("<li id='"+ i +"' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
        } else if (i < totalPages) {
            $(".pagination").append("<li id='"+ i +"' style='display:none;' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
        }
    }
    $(".pagination").append("<li id='dot-3' style='display:none;' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");
    $(".pagination").append("<li id='"+ totalPages +"' class='current-page temp-button'><a href='javascript:void(0)'>" + totalPages + "</a></li>");
    $(".pagination").append("<li id='next-page' class='temp-button'><a href='javascript:void(0)' aria-label='Next'><span aria-hidden='true'>&raquo;</span></a></li>");
}
