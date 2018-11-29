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

function pagination() {
    var numberOfItems = $(" #loop .list-group").length;
    if (numberOfItems > 10) {
        var limitPerPage = $("#selected-default").val();

        $("#selected-option").change(function() {
            var o = $(this).find("option:selected");
            if (o.val() === "All") {
                limitPerPage = numberOfItems;
            } else {
                limitPerPage = o.val()
            }

            $(".pagination").children("li.to-remove").remove();

            var totalPages = Math.ceil(numberOfItems / limitPerPage);

            createButtons(totalPages, limitPerPage);

            // When a new limit is selected, we reset the current page to one, since if we have 10 pages, and then
            // we changed to only having one page, we can't keep whatever page we were previously on (if it was greater
            // than 1) so we instead just set it to 1.
            var currentPage = 1;

            var grandTotal = limitPerPage * currentPage;

            for (var i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
                $("#loop .list-group:eq(" + i + ")").show();
            }

            switchPages(limitPerPage);

            nextPage(totalPages, limitPerPage);

        });

        var totalPages = Math.ceil(numberOfItems / limitPerPage);

        createButtons(totalPages, limitPerPage);

        switchPages(limitPerPage);

        nextPage(totalPages, limitPerPage);

        previousPage(totalPages, limitPerPage);
    }
}

function nextPage(totalPages, limitPerPage) {
    $("#next-page").on("click", function() {
        var currentPage = $(".pagination li.active").index();
        if (currentPage === totalPages) {
            return false;
        } else {
            currentPage ++;
            $(".pagination li").removeClass("active");
            $("#loop .list-group").hide();

            var grandTotal = limitPerPage * currentPage;

            for (var i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
                $("#loop .list-group:eq(" + i + ")").show();
            }
            $(".pagination li.current-page:eq(" + (currentPage - 1) + ")").addClass("active");
        }
    });
}

function previousPage(totalPages, limitPerPage) {
    $("#previous-page").on("click", function() {
        var currentPage = $(".pagination li.active").index();
        if (currentPage === 1) {
             return false;
        } else {
             currentPage --;
             $(".pagination li").removeClass('active');
             $("#loop .list-group").hide();

             var grandTotal = limitPerPage * currentPage;

             for (var i = grandTotal - limitPerPage; i < grandTotal; i++) {
                 $("#loop .list-group:eq(" + i + ")").show();
             }
             $(".pagination li.current-page:eq(" + (currentPage - 1) + ")").addClass('active');
         }
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
            $("#loop .list-group").hide();

            var grandTotal = limitPerPage * currentPage;

            for (var i = grandTotal - limitPerPage; i < grandTotal ; i ++) {
                $("#loop .list-group:eq(" + i + ")").show();
            }
        }
    });
}

function createButtons(totalPages, limitPerPage) {
    $(" #loop .list-group:gt(" + (limitPerPage - 1) + ")").hide();

    $(".pagination").append("<li class='current-page active to-remove'><a href='javascript:void(0)'>" + 1 + "</a></li>");

    for (var i = 2; i <= totalPages; i++){
        $(".pagination").append("<li class='current-page to-remove'><a href='javascript:void(0)'>" + i + "</a></li>")
    }
    $(".pagination").append("<li id='next-page' class='to-remove'><a href='javascript:void(0)' aria-label='Next'><span aria-hidden='true'>&raquo;</span></a></li>");
}