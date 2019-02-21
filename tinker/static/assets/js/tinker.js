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
// ~~~~~~~~~~~~~ For a specific example look at the comments of the function switchPageClick(limitPerPage) ~~~~~~~~~~~~~
let maxPages = 0;
function pagination(type) {
    let numberOfItems = $(" #loop .items-to-paginate").length;
    if (numberOfItems > 10) {
        let limitPerPage = 10;
        if (Cookies.get(type + "-cookie") != null) {
            limitPerPage = Cookies.get(type + "-cookie");
        }
        Cookies.set(type + "-cookie", limitPerPage, { expires: 365, path: '/' });

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
            Cookies.set(type + "-cookie", limitPerPage, { expires: 30, path: '/' });

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
        });

        let totalPages = Math.ceil(numberOfItems / limitPerPage);
        maxPages = totalPages;

        createButtons(limitPerPage);

        switchPageClick(limitPerPage);

        nextOrPreviousPage(limitPerPage, "next-page");

        nextOrPreviousPage(limitPerPage, "previous-page");
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
                // This statement works just like the "if (currentPage === 1)" below since we don't want to go over
                // the maximum number of valid pages, so we make it return false if we click next and already on the
                // last valid page
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
            // if currentPage = 2 or 6 or totalPages + 2, then it means that those are ... buttons, and since we don't
            // want to ever be on a ... button (since they are useless besides for organization) we use this if, else
            // to skip over them instead of landing on them
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
            // if the totalPages < paginationRange, we don't have to worry about dealing with the ... buttons, so we can
            // just do everything normally
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

// This method switches the page when you click on a button
// I had an error before when my function header was "switchPageClick(limitPerPage, totalPages)" that whenever the limit
// was changed, the "totalPages" variable would still be set to the old one, thus making it possible to go to pages
// that weren't valid for the new limit. I overcame this by creating a variable called "maxPages" which is at a overseeing
// scope level over the pagination function and whenever the "totalPages" variable changes, "maxPages" is set to it and
// then we can just use "maxPages" here in alternative to "totalPages"
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
    // The code below display 1 as a button [1] and makes it visible since we always want it to be visible
    $(".pagination").append("<li id='1' class='current-page active temp-button'><a href='javascript:void(0)'>" + 1 + "</a></li>");

    // The ... only occurs when there are more pages than the paginationRange, currently paginationRange is set to 10,
    // but should be able to be changed by just changing what paginationRange is set to.
    if (totalPages > paginationRange) {
        // This code adds in a ... right after 1 but it is currently invisible since we won't use it yet.
        $(".pagination").append("<li id='dot-1' style='display:none;' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");
        for (let i = 2; i <= totalPages; i++) {
            // We iterate through 2-totalPages since we need pages 2 - totalPages now
            if (i > 4 && i < (totalPages - 3)) {
                if (i === 5) {
                    // this adds the 2nd dot after 4 that is used for the ... portion when pages < 4
                    $(".pagination").append("<li id='dot-2' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");
                }
                // this adds the button page = 5, but invisible since we don't need it yet
                $(".pagination").append("<li id='" + i + "' style='display:none;' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
            } else if (i < 5) {
                // if i is less than 5, meaning this is going to show pages 2-4, we want them to be visible, so that is
                // why its in its own else if
                $(".pagination").append("<li id='" + i + "' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
            } else if (i < totalPages) {
                // and if we missed any pages, this method adds them and displays them as none since they aren't one of
                // the pages we want visible to start
                $(".pagination").append("<li id='" + i + "' style='display:none;' class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
            }
        }
        // This adds [...][totalPages] to the select and makes the [...] invisible and the [totalPages] visible since
        // we always want to see it
        $(".pagination").append("<li id='dot-3' style='display:none;' class='dot current-page temp-button'><a href='javascript:void(0)'>...</a></li>");
        $(".pagination").append("<li id='" + totalPages + "' class='current-page temp-button'><a href='javascript:void(0)'>" + totalPages + "</a></li>");

    } else {
        // If totalPages is less than paginationRange, then we don't need to worry about adding dots, so we just add
        // every button like normal
        for (let i = 2; i <= totalPages; i++) {
             $(".pagination").append("<li id='" + i + "'  class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
        }
    }
    // We finally add on the next button
    $(".pagination").append("<li id='next-page' class='temp-button'><a href='javascript:void(0)' aria-label='Next'><span aria-hidden='true'>&raquo;</span></a></li>");
}
