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
        if (Cookies.get('e-announcement-cookie') != null) {
            limitPerPage = Cookies.get('e-announcement-cookie');
        } else {
            Cookies.set('e-announcement-cookie', limitPerPage, { expires: 30, path: '/' });
        }

        if (limitPerPage == 10) {
            $("#selected-option").html("<option value=\"10\" selected='selected'>10</option>\n" +
                "<option value=\"20\">20</option>\n" +
                "<option value=\"50\">50</option>\n" +
                "<option value=\"{{ search_results|length }}\">All</option>");
        }else if (limitPerPage == 20) {
            $("#selected-option").html("<option value=\"10\">10</option>\n" +
                    "<option value=\"20\" selected='selected'>20</option>\n" +
                    "<option value=\"50\">50</option>\n" +
                    "<option value=\"{{ search_results|length }}\">All</option>");
        }else if (limitPerPage == 50) {
            $("#selected-option").html("<option value=\"10\">10</option>\n" +
                "<option value=\"20\">20</option>\n" +
                "<option value=\"50\" selected='selected'>50</option>\n" +
                "<option value=\"{{ search_results|length }}\">All</option>");
        }else {
            $("#selected-option").html("<option value=\"10\">10</option>\n" +
                "<option value=\"20\">20</option>\n" +
                "<option value=\"50\">50</option>\n" +
                "<option value=\"{{ search_results|length }}\" selected='selected'>All</option>");
        }

        $("#selected-option").change(function() {
            limitPerPage = $("#selected-option").children("option:selected").attr("value");
            Cookies.set('e-announcement-cookie', limitPerPage, { expires: 30, path: '/' });

            if (limitPerPage == 10) {
                $("#selected-option").html("<option value=\"10\" selected='selected'>10</option>\n" +
                    "<option value=\"20\">20</option>\n" +
                    "<option value=\"50\">50</option>\n" +
                    "<option value=\"{{ search_results|length }}\">All</option>");
            }else if (limitPerPage == 20) {
                $("#selected-option").html("<option value=\"10\">10</option>\n" +
                        "<option value=\"20\" selected='selected'>20</option>\n" +
                        "<option value=\"50\">50</option>\n" +
                        "<option value=\"{{ search_results|length }}\">All</option>");
            }else if (limitPerPage == 50) {
                $("#selected-option").html("<option value=\"10\">10</option>\n" +
                    "<option value=\"20\">20</option>\n" +
                    "<option value=\"50\" selected='selected'>50</option>\n" +
                    "<option value=\"{{ search_results|length }}\">All</option>");
            }else if (limitPerPage == numberOfItems) {
                $("#selected-option").html("<option value=\"10\">10</option>\n" +
                    "<option value=\"20\">20</option>\n" +
                    "<option value=\"50\">50</option>\n" +
                    "<option value=\"{{ search_results|length }}\" selected='selected'>All</option>");
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

            switchPages(limitPerPage);

            nextOrPreviousPage(totalPages, limitPerPage, "next-page");

        });

        var totalPages = Math.ceil(numberOfItems / limitPerPage);

        createButtons(totalPages, limitPerPage);

        switchPages(limitPerPage);

        nextOrPreviousPage(totalPages, limitPerPage, "next-page");

        nextOrPreviousPage(totalPages, limitPerPage, "previous-page");
    }
}

function nextOrPreviousPage(totalPages, limitPerPage, type) {
    $("#" + type +" ").on("click", function() {
        var currentPage = $(".pagination li.active").index();
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

        var grandTotal = limitPerPage * currentPage;

        for (var i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
            $("#loop .items-to-paginate:eq(" + i + ")").show();
        }
        $(".pagination li.current-page:eq(" + (currentPage - 1) + ")").addClass("active");
    });
}

function switchPages(limitPerPage) {
    $(".pagination li.current-page").on("click", function() {
        if ($(this).hasClass("active")) {
            return false;
        } else {
            var currentPage = $(this).index();
            $(".pagination li").removeClass("active");
            $(this).addClass("active");
            $("#loop .items-to-paginate").hide();

            var grandTotal = limitPerPage * currentPage;

            for (var i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
                $("#loop .items-to-paginate:eq(" + i + ")").show();
            }
        }
    });
}

function createButtons(totalPages, limitPerPage) {
    $(" #loop .items-to-paginate:gt(" + (limitPerPage - 1) + ")").hide();

    $(".pagination").append("<li class='current-page active temp-button'><a href='javascript:void(0)'>" + 1 + "</a></li>");

    for (var i = 2; i <= totalPages; i++){
        $(".pagination").append("<li class='current-page temp-button'><a href='javascript:void(0)'>" + i + "</a></li>");
    }
    $(".pagination").append("<li id='next-page' class='temp-button'><a href='javascript:void(0)' aria-label='Next'><span aria-hidden='true'>&raquo;</span></a></li>");
}