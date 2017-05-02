exports.is_date_a_bethel_holiday = function is_date_a_bethel_holiday(date) {
    function isDateFridayBeforeEaster(date) {
        var Y = date.getFullYear();

        // crazy code to determine easter day
        var C = Math.floor(Y/100);
        var N = Y - 19*Math.floor(Y/19);
        var K = Math.floor((C - 17)/25);
        var I = C - Math.floor(C/4) - Math.floor((C - K)/3) + 19*N + 15;
        I = I - 30*Math.floor((I/30));
        I = I - Math.floor(I/28)*(1 - Math.floor(I/28)*Math.floor(29/(I + 1))*Math.floor((21 - N)/11));
        var J = Y + Math.floor(Y/4) + I + 2 - C + Math.floor(C/4);
        J = J - 7*Math.floor(J/7);
        var L = I - J;
        var M = 3 + Math.floor((L + 40)/44);
        var D = L + 28 - 31*Math.floor(M/4);
        // test
        var M_zero_based = M - 1;

        // The -2 is to check if it is the friday before easter
        return date.getMonth() == M_zero_based && date.getDate() == (D-2);
    }

    // Months are zero based indexing
    // New Years Day
    if( date.getMonth() == 0 && date.getDate() == 1)
        return true;
    // New Years(observed) -- If new years day is on the weekend, we get the monday off (2nd or 3rd)
    else if( date.getMonth() == 0 && date.getDay() == 1 && (date.getDate() == 2 || date.getDate() == 3) )
        return true;
    // MLK Day - 3rd monday in jan
    else if( date.getMonth() == 0 && date.getDay() == 1 && Math.ceil(date.getDate()/7) == 3 )
        return true;
    // Easter (is the date the friday before easter)
    else if( isDateFridayBeforeEaster(date) )
        return true;
    // memorial day - last monday in may (may, date is after 24th and its a monday)
    else if(date.getMonth() == 4 && date.getDate() > 24 && date.getDay() == 1 )
        return true;
    // july 4
    else if(date.getMonth() == 6 && date.getDate() == 4)
        return true;
    // Labor Day - first monday in sept
    else if( date.getMonth() == 8 && date.getDay() == 1 && Math.ceil(date.getDate()/7) == 1 )
        return true;
    // Thanksgiving and Black Friday -- 4th thursday in nov, 4th friday in nov
    else if( date.getMonth() == 10 && Math.ceil(date.getDate()/7) == 4 && (date.getDay() == 4 || date.getDay() == 5))
        return true;
    // Christmas Eve(observed) - christmas eve is on the weekend, we get the friday off (22nd or 23rd).
    else if( date.getMonth() == 11 && date.getDay() == 5 && (date.getDate() == 22 || date.getDate() == 23) )
        return true;
    // christmas days
    else if( date.getMonth() == 11 && date.getDate() >= 24)
        return true;

    return false;
}