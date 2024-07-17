document.addEventListener("DOMContentLoaded", function(){
    var activeTableBody = document.getElementById("activeTableBody");
    if (activeTableBody){
        originalRows = Array.from(activeTableBody.getElementsByTagName("tr"));
        allRows = originalRows.slice(); // copy the original rows
        updateTableDisplay();
    }
});

//gloable variables
var allRows = []
var originalRows = []
var currentPage = 0;
var pageSize = 10;

//function to sort the table based on the column
function sortTable(n) {
    var switching, i, t, shouldSwitch, dir, switchcount = 0;
    switching = true;
    table = document.getElementById("activeTable");
    // Set the sorting direction to ascending:
    dir = "asc";
    // Resst the sorting icon
    var allSortIcons = table.getElementsByClassName("sort-icon");
    for (t = 0; t < allSortIcons.length; t++) {
        allSortIcons[t].className = "fa-solid fa-sort sort-icon";
    }
    // Make a loop that will continue until no switching has been done:
    while (switching) {
        switching = false;
        for (i = 0; i < (allRows.length -1); i++) {
            shouldSwitch = false;
            var x = allRows[i].getElementsByTagName("td")[n]
            var y = allRows[i + 1].getElementsByTagName("td")[n]
            // Check if the cell contain number or string
            var xValue = handleInput(x.innerHTML || x.textContent);
            var yValue = handleInput(y.innerHTML || y.textContent);
            if (dir == "asc") {
                if (xValue > yValue){
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (xValue < yValue){
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            allRows.splice(i, 0, allRows.splice(i+1, 1)[0]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
    // update the sorting icon
    var sortIcon = table.rows[0].getElementsByTagName("th")[n].getElementsByClassName("sort-icon")[0];
    if (dir == "asc") {
        sortIcon.className = "fa-solid fa-sort-up sort-icon";
    } else {
        sortIcon.className = "fa-solid fa-sort-down sort-icon";
    }
    // update the allRows array after sorting
    updateTableDisplay();
}

function searchFilterTable() {
    var input = document.getElementById("filterInput");
    var filter = input.value.toUpperCase();
    allRows = originalRows.filter(row => {
        var isVisable = Array.from(row.getElementsByTagName("td")).some(td => td.innerHTML.toUpperCase().includes(filter)); // check if any cell in the row contains the filter
        return isVisable;
    })

    currentPage = 0;
    updateTableDisplay();
}

function updateTableDisplay() {
    var filteredRows = filterRows(allRows);
    var paginatedRows = paginateRows(filteredRows);
    renderTable(paginatedRows);
    updatePagination(filteredRows.length);
}

function filterRows(rows) {
    var headers = document.getElementById("activeTable").rows[0].cells;
    var typeIndex = -1;
    var activeFilter = document.getElementById("activeFilter"); // for user status
    var membershipFilter = document.getElementById("membershipFilter"); // for membership status
    var typeFilter = document.getElementById("typeFilter"); // for class or therapeutic type
    var attendanceFilter = document.getElementById("attendanceFilter"); // for attendance status
    var sessionAvailabilityFilter = document.getElementById("sessionAvailabilityFilter"); // for session availability
    var bookingFilter = document.getElementById("bookingFilter"); // for booking status
    var membersessionAvailabilityFilter = document.getElementById("membersessionAvailabilityFilter"); // for member session availability

    return rows.filter(row => {
        // check if the user status filter exists and if so, apply it
        if (activeFilter) {
            var userStatusFilter = activeFilter.value;
            var userStatusCell = row.cells[6];
            var userStatus = userStatusCell.textContent.trim();
            if (userStatusFilter === "active" && userStatus !== "Active") {
                return false
            } else if (userStatusFilter === "inactive" && userStatus !== "Inactive") {
                return false
            }
        }

        // check if the membership status filter exists and if so, apply it
        if (membershipFilter) {
            var membershipFilterValue = membershipFilter.value;
            var membershipStatusCell = row.cells[4];
            var membershipStatus = membershipStatusCell.textContent.trim();
            var expiryDateCell = row.cells[5];
            var expiryDate = new Date(expiryDateCell.getAttribute("data-date"));
            var today = new Date();
            var oneMonthFromToday = new Date().setMonth(today.getMonth() + 1);

            if (membershipFilterValue === "active" && membershipStatus !== "Active") {
                return false
            } else if (membershipFilterValue === "expired" && membershipStatus !== "Expired") {
                return false
            } else if (membershipFilterValue === "near_expired" && (membershipStatus !== "Active" || expiryDate <= oneMonthFromToday)) {
                return false
            }
        }

        // check if the type filter exists and if so, apply it
        if (typeFilter) {
            for (var i = 0; i < headers.length; i++) {
                if (headers[i].textContent.trim() === "Type") {
                    typeIndex = i;
                    break;
                }
            }
            if (typeIndex === -1) {
                console.error("Type column not found");
                return rows;
            }
            var typeFilterValue = typeFilter.value;
            var typeCell = row.cells[typeIndex]
            var type = typeCell.textContent.trim();

            if (typeFilterValue === "class" && type !== "Group Class") {
                return false
            } else if (typeFilterValue === "therapeutic" && type !== "Private Therapeutic") {
                return false
            }
        }

        // check if the attendance filter exists and if so, apply it
        if (attendanceFilter) {
            var attendanceFilterValue = attendanceFilter.value;
            var attendanceCell = row.cells[7]
            var attendance = attendanceCell.textContent.trim();

            if (attendanceFilterValue === "present" && attendance !== "Present") {
                return false
            } else if (attendanceFilterValue === "absent" && attendance !== "Absent") {
                return false
            }
        }

        // check if the session availability filter exists and if so, apply it
        if (sessionAvailabilityFilter) {
            var sessionAvailabilityFilterValue = sessionAvailabilityFilter.value;
            var sessionAvailabilityCell = row.cells[7]
            var sessionAvailability = sessionAvailabilityCell.textContent.trim();

            if (sessionAvailabilityFilterValue === "available" && sessionAvailability !== "Available") {
                return false
            } else if (sessionAvailabilityFilterValue === "fullyBooked" && sessionAvailability !== "Fully Booked") {
                return false
            }
        }

        // check if the booking filter exists and if so, apply it
        if (bookingFilter) {
            var bookingFilterValue = bookingFilter.value;
            var bookingCell = row.cells[5]
            var booking = bookingCell.textContent.trim();
            var bookingInnerHtml = bookingCell.innerHTML.trim();

            if (bookingFilterValue === "available" && !bookingInnerHtml.includes('<i class="fa-solid fa-xmark icon-color"></i>')) {
                return false
            } else if (bookingFilterValue === "expired" && booking !== "Expired") {
                return false
            }
        }

        // check if the membersession availability filter exists and if so, apply it
        if (membersessionAvailabilityFilter) {
            var membersessionAvailabilityFilterValue = membersessionAvailabilityFilter.value;
            var membersessionAvailabilityCell = row.cells[6]
            var membersessionAvailability = membersessionAvailabilityCell.textContent.trim();

            if (membersessionAvailabilityFilterValue === "available" && membersessionAvailability !== "Available") {
                return false
            } else if (membersessionAvailabilityFilterValue === "fullyBooked" && membersessionAvailability !== "Fully Booked") {
                return false
            }
        }

        return true;
    });
}

// function to paginate the table
function paginateRows(rows) {
    var start = currentPage * pageSize;
    var end = start + pageSize;
    return rows.slice(start, end);
}

// function to render the table
function renderTable(rows) {
    var tableBody = document.getElementById("activeTableBody");
    tableBody.innerHTML = "";

    var anyRowsVisable = rows.some(row => row.style.display !== "none")

    if (rows.length === 0 || !anyRowsVisable) {
        var noDataTr = document.createElement("tr");
        var noDataTd = document.createElement("td");
        var columnCount = document.getElementById("activeTable").rows[0].cells.length;
        noDataTd.colSpan = columnCount;
        noDataTd.textContent = "No data available after filter.";
        noDataTd.classList.add("text-center");
        noDataTr.appendChild(noDataTd);
        tableBody.appendChild(noDataTr);
    } else {
        rows.forEach(row => tableBody.appendChild(row));
    }
}

// function to update the pagination
function updatePagination(totalRows) {
    var totalPages = Math.ceil(totalRows/pageSize);
    var pagination = document.getElementById("pagination");

    // remove old page number links
    var firstButton = pagination.children[0];
    var lastButton = pagination.children[pagination.children.length - 1];
    pagination.innerHTML = "";
    pagination.appendChild(firstButton);


    for (let i=0; i<totalPages; i++) {
        var li = document.createElement("li");
        li.className = "page-item" + (i === currentPage ? " active" : "");
        var a = document.createElement("a");
        a.className = "page-link";
        a.href = "#";
        a.textContent = i + 1;
        a.onclick = (function(page) {
            return function() {
                currentPage = page;
                updateTableDisplay();
            };
        })(i);
        li.appendChild(a);
        pagination.appendChild(li);
    }
    // add last button
    pagination.appendChild(lastButton);
}

function goToFirstPage() {
    currentPage = 0;
    updateTableDisplay();
}

function goToLastPage() {
    currentPage = Math.ceil(allRows.length/pageSize) - 1;
    updateTableDisplay();
}

var pageSizeSelect = document.getElementById("pageSizeSelect")
if (pageSizeSelect) {
    pageSizeSelect.addEventListener("change", function(){
        pageSize = parseInt(this.value);
        currentPage = 0;
        updateTableDisplay();
    })
}

var typeFilter = document.getElementById("typeFilter");
var activeFilter = document.getElementById("activeFilter");
var membershipFilter = document.getElementById("membershipFilter");
var attendanceFilter = document.getElementById("attendanceFilter");
var sessionAvailabilityFilter = document.getElementById("sessionAvailabilityFilter");
var bookingFilter = document.getElementById("bookingFilter");
var membersessionAvailabilityFilter = document.getElementById("membersessionAvailabilityFilter");

[typeFilter, activeFilter, membershipFilter, attendanceFilter, sessionAvailabilityFilter, bookingFilter, membersessionAvailabilityFilter].forEach(filter => {
    if (filter) {
        filter.addEventListener("change", function() {
            currentPage = 0;
            updateTableDisplay();
        });
    }
});

// // user active table filter
// function filterUserStatus() {
//     var filter = document.getElementById("activeFilter").value;
//     var tableBody = document.getElementById("activeTableBody");
//     var rows = tableBody.getElementsByTagName("tr");

//     for (var i = 0; i<rows.length; i++) {
//         var userStatusCell = rows[i].cells[6]
//         var userStatus = userStatusCell.textContent.trim();

//         switch(filter) {
//             case "active":
//                 rows[i].style.display = (userStatus === "Active") ? "" : "none";
//                 break;
//             case "inactive":
//                 rows[i].style.display = (userStatus === "Inactive") ? "" : "none";
//                 break;
//             default:
//                 rows[i].style.display = "";
//                 break;
//         }
//     }
// }
// document.getElementById("activeFilter").addEventListener("change", filterUserStatus);


// // Membership table filter
// function filterMembershipStatus() {
//     var filter = document.getElementById("membershipFilter").value;
//     var tableBody = document.getElementById("activeTableBody");
//     var rows = tableBody.getElementsByTagName("tr");

//     for (var i = 0; i<rows.length; i++) {
//         var statusCell = rows[i].cells[4]
//         var expiryDateCell = rows[i].cells[5]
//         var status = statusCell.textContent.trim();
//         var expiryDate = new Date(expiryDateCell.textContent.trim());
//         var today = new Date();
//         var oneMonthFromToday = new Date().setMonth(today.getMonth() + 1);

//         switch(filter) {
//             case "active":
//                 rows[i].style.display = (status === "Active") ? "" : "none";
//                 break;
//             case "expired":
//                 rows[i].style.display = (status === "Expired") ? "" : "none";
//                 break
//             case "near_expired":
//                 rows[i].style.display = (status === "Active" && expiryDate < oneMonthFromToday) ? "" : "none";
//                 break;
//             default:
//                 rows[i].style.display = "";
//                 break;
//         }
//     }
// }
// document.getElementById("membershipFilter").addEventListener("change", filterMembershipStatus);

//Helper function to handle input for sorting
// function handleInput(inputText) {
//     // remove dollar sign
//     var cleanedText = inputText.replace(/[$,]/g, '');

//     if (!isNaN(cleanedText)) {
//         return parseFloat(cleanedText);
//     }

//     // check if the input is a time range like 09:00 - 10:00
//     if (inputText.includes(' - ') && inputText.match(/^\d{2}:\d{2} - \d{2}:\d{2}$/)) {
//         var timePatrs = inputText.split(' - ');
//         var startTimeParts = timePatrs[0].split(':');
//         var startHour = parseInt(startTimeParts[0], 10);
//         var startMinute = parseInt(startTimeParts[1], 10);
//         return new Date(1970, 0, 1, startHour, startMinute);
//     } else {
//         // check if the input is a date like 01-01-2024 09:00 - 10:00 
//         var parts = inputText.split(' ');
//         if (parts[0].match(/^\d{2}-\d{2}-\d{4}$/)) {
//             var dateParts = parts[0].split('-')
//             var year = parseInt(dateParts[2], 10);
//             var month = parseInt(dateParts[1], 10) - 1;
//             var day = parseInt(dateParts[0], 10);
//             if (parts.length > 1 && parts[1].match(/^\d{2}:\d{2}$/)) {
//                 // time part exists
//                 var timePatrs = parts[1].split(':');
//                 var hour = parseInt(timePatrs[0], 10);
//                 var minute = parseInt(timePatrs[1], 10);
//                 return new Date(year, month, day, hour, minute);
//             } else {
//                 return new Date(year, month, day);
//             }
//         } else {
//             return inputText.toLowerCase();
//         }
//     }
// }

//Helper function to handle input for sorting
function handleInput(inputText) {
    // remove dollar sign
    var cleanedText = inputText.replace(/[$,]/g, '');

    // try to extract number from the text
    var matches = cleanedText.match(/(\d+)/);
    if (matches) {
        var numberPart = parseFloat(matches[0]);
        if (!isNaN(numberPart) && cleanedText.match(/^\d+$/)) {
            return numberPart;
        }
    }

    // check if the input is a time range like 09:00 - 10:00
    if (inputText.includes(' - ') && inputText.match(/^\d{2}:\d{2} - \d{2}:\d{2}$/)) {
        var timePatrs = inputText.split(' - ');
        var startTimeParts = timePatrs[0].split(':');
        var startHour = parseInt(startTimeParts[0], 10);
        var startMinute = parseInt(startTimeParts[1], 10);
        return new Date(1970, 0, 1, startHour, startMinute);
    } 
    
    // check if the input is a date like 01-01-2024 09:00 - 10:00 
    var parts = inputText.split(' ');
    if (parts[0].match(/^\d{2}-\d{2}-\d{4}$/)) {
        var dateParts = parts[0].split('-')
        var year = parseInt(dateParts[2], 10);
        var month = parseInt(dateParts[1], 10) - 1;
        var day = parseInt(dateParts[0], 10);
        if (parts.length > 1 && parts[1].match(/^\d{2}:\d{2}$/)) {
            // time part exists
            var timePatrs = parts[1].split(':');
            var hour = parseInt(timePatrs[0], 10);
            var minute = parseInt(timePatrs[1], 10);
            return new Date(year, month, day, hour, minute);
        } else {
            return new Date(year, month, day);
        }
    }

    // for handling cases like 'xx minutes' 
    if (numberPart && isNaN(parseFloat(inputText))) {
        return numberPart;
    }

    // return ther input as lower case
    return inputText.toLowerCase();
}