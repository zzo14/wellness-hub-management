document.addEventListener("DOMContentLoaded", function(){
    formatDateToNZ();
    allRows = Array.from(document.getElementById("activeTableBody").getElementsByTagName("tr"));
    updateTableDisplay();
});
document.getElementById("sortSelect").addEventListener("change", sortTableBasedOnSelection);

//gloable variables
var allRows = []
var currentPage = 0;
var pageSize = 1;

function sortTableBasedOnSelection() {
    var sortCriteria = document.getElementById("sortSelect").value;
    var columnForPayerName = 2; 
    var columnForDate = 5; 
    var columnForAmount = 6; 

    allRows.sort(function(a, b) {
        
        switch (sortCriteria) {
            case "payerNameAsc":
                return a.cells[columnForPayerName].textContent.localeCompare(b.cells[columnForPayerName].textContent);
            case "payerNameDesc":
                return b.cells[columnForPayerName].textContent.localeCompare(a.cells[columnForPayerName].textContent);
            case "paymentDateNewest":
                return new Date(b.cells[columnForDate].textContent) - new Date(a.cells[columnForDate].textContent);
            case "paymentDateOldest":
                return new Date(a.cells[columnForDate].textContent) - new Date(b.cells[columnForDate].textContent);
            case "paymentAmountAsc":
                return parseFloat(a.cells[columnForAmount].textContent) - parseFloat(b.cells[columnForAmount].textContent);
            case "paymentAmountDesc":
                return parseFloat(b.cells[columnForAmount].textContent) - parseFloat(a.cells[columnForAmount].textContent);
            default:
                break;
        }
    });

    updateTableDisplay(); 
}

function serachFilterTable() {
    var input = document.getElementById("filterInput");
    var filter = input.value.toUpperCase();

    //filter table based on the input
    allRows.forEach(row => {
        var isVisable = Array.from(row.getElementsByTagName("td")).some(td => td.innerHTML.toUpperCase().indexOf(filter) > -1);
        row.style.display = isVisable ? "" : "none";
    })
    updateTableDisplay();
}

function updateTableDisplay() {
    var filteredRows = filterRows(allRows);
    var paginatedRows = paginateRows(filteredRows);
    renderTable(paginatedRows);
    updatePagination(filteredRows.length);
}

function filterRows(rows) {
    var activeFilter = document.getElementById("activeFilter");
    var membershipFilter = document.getElementById("membershipFilter");


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
            var expiryDate = new Date(expiryDateCell.textContent.trim());
            var today = new Date();
            var oneMonthFromToday = new Date().setMonth(today.getMonth() + 1);

            if (membershipFilterValue === "active" && membershipStatus !== "Active") {
                return false
            } else if (membershipFilterValue === "expired" && membershipStatus !== "Expired") {
                return false
            } else if (membershipFilterValue === "near_expired" && (membershipStatus !== "Active" || expiryDate >= oneMonthFromToday)) {
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
    rows.forEach(row => tableBody.appendChild(row));
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
        a.style.backgroundColor = "#198754";
        a.style.border = "1px solid #198754";
        a.style.color = "white";  
        a.onclick = (function(page) {
            return function() {
                console.log(page);
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

document.getElementById("pageSizeSelect").addEventListener("change", function(){
    pageSize = parseInt(this.value);
    currentPage = 0;
    updateTableDisplay();
})
document.getElementById("activeFilter").addEventListener("change", updateTableDisplay);
document.getElementById("membershipFilter").addEventListener("change", updateTableDisplay);

// set max datepicker date to today
function max_date_today() {
    var today = new Date().toISOString().split('T')[0];
    document.getElementById('date_of_birth').max = today;
}

//format date to NZ format
function formatDateToNZ() {
    var dateElements = document.querySelectorAll(".formatedDate")

    dateElements.forEach(function(element) {
        var dateString = element.getAttribute("data-date")
        var year = dateString.split("-")[0];
        var month = dateString.split("-")[1].padStart(2, "0");
        var day = dateString.split("-")[2].padStart(2, "0");

        element.innerText = day + "/" + month + "/" + year;
    })
}

// Toggle password visibility
function toggle_password_visibility(password_id) {
    var passwordInput = document.getElementById(password_id);
    var isVisibility = passwordInput.type === 'text';
    passwordInput.type = isVisibility ? 'password' : 'text';
    var toggle_icon = passwordInput.nextElementSibling.querySelector('i');
    toggle_icon.className = isVisibility ? 'fa-regular fa-eye' : 'fa-regular fa-eye-slash';

    // Update aria-label or title for screen readers
    var actionText = isVisibility ? 'Show Password' : 'Hide Password';
    passwordInput.nextElementSibling.setAttribute('aria-label', actionText);
    passwordInput.nextElementSibling.setAttribute('title', actionText);
};

// change password input border color based on password complexity and enable/disable submit button
function validate_password(password_id, tooltip_id) {
    var passwordInput = document.getElementById(password_id);
    var tooltip = document.getElementById(tooltip_id)
    var submitButton = passwordInput.form.querySelector('button[type=submit]')
    var pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z\d]).{8,}$/;

    if (passwordInput.value === '') {
        passwordInput.style.borderColor = '';
        tooltip.style.display = 'none';
        submitButton.disabled = false;
    }
    else if (pattern.test(passwordInput.value)) {
        passwordInput.style.borderColor = 'green';
        tooltip.style.display = 'none';
        submitButton.disabled = false;
    } else {
        passwordInput.style.borderColor = 'red';
        tooltip.style.display = 'block';
        submitButton.disabled = true;
    }
}