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

// This variable sets how many pages are necessary to make it paginate
const paginationRange = 10;
// maxPages is up here since it looks like a lot of variables were getting confused as to what the variable "totalPages"
// was suppose to be set to since it always used the old version after the limit was changed. So in order to fix this
// issue, I made this variable "maxPages" with overseeing scope and whenever "totalPages" changes I set "maxPages" equal
// to it and just hand the functions that need "totalPages" the "maxPage" variable.
// ~~~~~~~~~~~~~~~~ For a specific example look at the comments of the function goToPage(limitPerPage) ~~~~~~~~~~~~~~~~~
let maxPages = 0;
function pagination(type) {
    let numberOfItems = $(" #loop .items-to-paginate").length;
    if (numberOfItems > 10) {
        let limitPerPage = 10;
        if (Cookies.get(type) != null) {
            limitPerPage = Cookies.get(type);
        }
        Cookies.set(type, limitPerPage, { expires: 365, path: '/' });

        let limitList = [10, 25, 50, numberOfItems]

        // This loop here iterates through the list of limit values and sets the selected value
        for (let i = 0; i < limitList.length; i ++) {
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
                Cookies.set('e-announcement', limitPerPage, { expires: 30, path: '/' });
            } else if (type == 'event') {
                Cookies.set('event', limitPerPage, { expires: 30, path: '/' });
            }

            $(".pagination").children("li.temp-button").remove();

            let totalPages = Math.ceil(numberOfItems / limitPerPage);
            maxPages = totalPages;

            createButtons(totalPages, limitPerPage);

            // When a new limit is selected, we reset the current page to one, since if we have 10 pages, and then
            // we changed to only having one page, we can't keep whatever page we were previously on (if it was greater
            // than 1) so we instead just set it to 1.
            let currentPage = 1;

            let grandTotal = limitPerPage * currentPage;

            for (let i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
                $("#loop .items-to-paginate:eq(" + i + ")").show();
            }

            switchPageClick(limitPerPage);

            nextOrPreviousPage(limitPerPage, "next-page");

            goToPage(limitPerPage);
        });

        let totalPages = Math.ceil(numberOfItems / limitPerPage);
        maxPages = totalPages;

        createButtons(limitPerPage);

        switchPageClick(limitPerPage);

        nextOrPreviousPage(limitPerPage, "next-page");

        nextOrPreviousPage(limitPerPage, "previous-page");

        goToPage(limitPerPage);
    }
}
// Sets the next or previous page depending on what button you pressed
function nextOrPreviousPage(limitPerPage, type) {
    $("#" + type + " ").on("click", function () {
        let currentPage = $(".pagination li.active").index();
        let totalPages = maxPages;

        if (totalPages > paginationRange) {
            // Increments or decrements the currentPage depending on which button was pressed
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

            // This skips over the "..." li elements so they aren't set to active
            if (type === "next-page") {
                if (currentPage == 2) {
                    currentPage++;
                } else if (currentPage == 6) {
                    currentPage++;
                } else if (currentPage == totalPages + 2) {
                    currentPage++;
                }
            } else if (type === "previous-page") {
                if (currentPage == 2) {
                    currentPage--;
                } else if (currentPage == 6) {
                    currentPage--;
                } else if (currentPage == totalPages + 2) {
                    currentPage--;
                }
            }
            $(".pagination li.current-page:eq(" + (currentPage - 1) + ")").addClass("active");
            switchPages(limitPerPage, currentPage, type);
        } else {
            if (type === "next-page") {
                if (currentPage === totalPages) {
                    return false;
                } else {
                    currentPage ++;
                }
            } else if (type === "previous-page") {
                if (currentPage === 1) {
                    return false;
                } else {
                    currentPage --;
                }
            }
            $(".pagination li").removeClass("active");
            $("#loop .items-to-paginate").hide();

            let grandTotal = limitPerPage * currentPage;

            for (let i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
                $("#loop .items-to-paginate:eq(" + i + ")").show();
            }
            $(".pagination li.current-page:eq(" + (currentPage - 1) + ")").addClass("active");
        }
    });
}

// This method changes the page when you input a page number and click "Go"
// I had an error before when my function header was "goToPage(limitPerPage, totalPages)" that whenever the limit
// was changed, the "totalPages" variable would still be set to the old one, thus making it possible to go to pages
// that weren't valid for the new limit. I overcame this by creating a variable called "maxPages" which is at a overseeing
// scope level over the pagination function and whenever the "totalPages" variable changes, "maxPages" is set to it and
// then we can just use "maxPages" here in alternative to "totalPages"
function goToPage(limitPerPage) {
    $("button#go-to-button").on("click", function() {
        let totalPages = maxPages;
        let page = document.getElementById("go-to-input");
        let value = Math.floor(page.value);
        if (value > 0 && value < totalPages + 1 && totalPages > paginationRange) {
            $(".pagination li").removeClass("active");
            let currentPage = value;
            if (currentPage < 2) {
                currentPage = currentPage - 1;
            } else if (currentPage == totalPages) {
                currentPage = currentPage + 2;
            } else if (currentPage >= 5) {
                currentPage = currentPage + 1;
            }
            $(".pagination li.current-page:eq(" + (currentPage) + ")").addClass("active");
            switchPages(limitPerPage, Math.floor(page.value), "other");
            page.value = "";
        } else if (value > 0 && value < totalPages + 1) {
            $(".pagination li").removeClass("active");
            $(".pagination li.current-page:eq(" + (value - 1) + ")").addClass("active");
            page.value = "";
        } else {
            return ;
        }
    });
}

// This method switches the page when you click on a button
function switchPageClick(limitPerPage) {
    $(".pagination li.current-page").on("click", function() {
        if ($(this).hasClass("active")) {
            return false;
        } else {
            let currentPage = $(this).text();
            $(".pagination li").removeClass("active");
            $(this).addClass("active");
            switchPages(limitPerPage, currentPage, "other")
        }
    });
}

// This method hands off the current page to the showHideButtons function when a new button is either clicked or inputted
function switchPages(limitPerPage, currentPage, type) {
    let totalPages = maxPages;
    $("#loop .items-to-paginate").hide();
    let grandTotal = limitPerPage * currentPage;
    // If the next or previous button was pressed, this is how we make sure the "..." li elements aren't holding real data
    if (type === "next-page" || type === "previous-page") {
        if (currentPage < 2) {
            for (let i = grandTotal - limitPerPage; i < grandTotal; i++) {
                $("#loop .items-to-paginate:eq(" + i + ")").show();
            }
        } else if (currentPage > 2 && currentPage < 6) {
            for (let i = grandTotal - limitPerPage - 10; i < grandTotal - 10; i++) {
                $("#loop .items-to-paginate:eq(" + i + ")").show();
            }
        } else if (currentPage > 6 && currentPage < totalPages - 3) {
            for (let i = grandTotal - limitPerPage - 20; i < grandTotal - 20; i++) {
                $("#loop .items-to-paginate:eq(" + i + ")").show();
            }
        } else {
            for (let i = grandTotal - limitPerPage - 30; i < grandTotal - 30; i++) {
                $("#loop .items-to-paginate:eq(" + i + ")").show();
            }
        }
    } else {
        for (let i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
            $("#loop .items-to-paginate:eq(" + i + ")").show();
        }
    }

    // This is how we make sure the right button will be show in the right space when passed into showHideButtons
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
    if (type === "next-page" || type === "previous-page") {
        if (currentPage > totalPages && currentPage < totalPages + 3) {
            currentPage -= 1;
        }
        if (currentPage > 3) {
            currentPage -= 2;
        }
    }
    if (totalPages > paginationRange) {
        showHideButtons(currentPage);
    }
}

// This method makes the correct buttons show when you select a new button
function showHideButtons(currentPage) {
    let totalPages = maxPages;
    let x = (document.getElementsByClassName("temp-button")[currentPage - 1]).id;

    if ((x.split('-')[1]) == 1 || currentPage < 5) {
        for (let i = 1; i < totalPages; i++) {
            display([i.toString()],[]);
            if ((i > 0) && (i < 5)) {
                display([], [i.toString()]);
            }
        }
        display(["dot-1", "dot-3"], ["dot-2"]);
    } else if ((x.split('-')[1]) == 4 || currentPage > totalPages - 1) {
        for (let i = 2; i < totalPages; i++) {
            display([i.toString()],[]);
            if ((i > totalPages - 4)) {
                display([], [i.toString()]);
            }
        }
        display(["dot-1", "dot-3"], ["dot-2"]);
    } else {
        for (let i = 2; i < totalPages; i++) {
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
        for (let i = 0; i < none.length; i++) {
            document.getElementById(none[i].toString()).style.display = "none";
        }
    }
    if (inline.length !== 0) {
        for (let i = 0; i < inline.length; i ++) {
            document.getElementById(inline[i].toString()).style.display = "inline";
        }
    }
}

// This method creates all the initial buttons for pagination, along with the dots
function createButtons(limitPerPage) {
    let totalPages = maxPages;

    $(" #loop .items-to-paginate:gt(" + (limitPerPage - 1) + ")").hide();

    $(".pagination").append("<li id='1' class='current-page active temp-button'><a href='javascript:void(0)'>" + 1 + "</a></li>");

    if (totalPages > paginationRange) {
        $(".pagination").append("<li id='dot-1' style='display:none;' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");

        for (let i = 2; i <= totalPages; i++) {
            if (i > 4 && i < (totalPages - 3)) {
                if (i > 4 && i < 6 && totalPages > 6) {
                    $(".pagination").append("<li id='dot-2' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");
                }
                $(".pagination").append("<li id='" + i + "' style='display:none;' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
            } else if (i < 5) {
                $(".pagination").append("<li id='" + i + "' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
            } else if (i < totalPages) {
                $(".pagination").append("<li id='" + i + "' style='display:none;' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
            }
        }
        $(".pagination").append("<li id='dot-3' style='display:none;' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");
        $(".pagination").append("<li id='" + totalPages + "' class='current-page temp-button'><a href='javascript:void(0)'>" + totalPages + "</a></li>");

    } else {
        for (let i = 2; i <= totalPages; i++) {
             $(".pagination").append("<li id='" + i + "'  class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
        }
    }
    $(".pagination").append("<li id='next-page' class='temp-button'><a href='javascript:void(0)' aria-label='Next'><span aria-hidden='true'>&raquo;</span></a></li>");
}
