document.addEventListener('DOMContentLoaded', function() {
    // Initialize the timetable
    filterTherapistClass();
});

var calendar;
let debouceTimeout;

function filterTherapistClass() {
    var therapistId = document.getElementById("therapist-id");
    if (therapistId) {
        therapistId = therapistId.value;
    }
    var isChecked = document.getElementById("filterTherapist");
    if (isChecked) {
        isChecked = isChecked.checked;
    }
    var filteredData;
    if (isChecked) {
        filteredData = timetableData.filter(function(c) {
            return c.therapistId == therapistId
        });
    } else {
        filteredData = timetableData;
    }
    initTimetable(filteredData);
}

function serachFilterTimetable() {
    clearTimeout(debouceTimeout);
    debouceTimeout = setTimeout(function() {
        var input = document.getElementById("filterInput");
        var filter = input.value.toUpperCase();
        var filteredData = timetableData.filter(function(c) {
            return c.title.toUpperCase().includes(filter)
        });
        initTimetable(filteredData);
    }, 300);
}


// Initialize the timetable with classes
function initTimetable(classes) {
    var calendarEl = document.getElementById('calendar');
    if (!calendar) {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            fixedWeekCount: false,
            headerToolbar: {
                left: 'prev next today',
                center: 'title',
                right: 'dayGridMonth timeGridWeek timeGridDay'
            }, 
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true,
            },
            events: classes,
            eventDidMount: function(info) {
                // Hide the event if it is in the past
                if (info.event.start < new Date()) {
                    info.el.style.display = 'none';
                }
                // Add a tooltip to show the event title
                var tooltip = new bootstrap.Tooltip(info.el, {
                    title: info.event.title,
                    placement: 'top',
                    trigger: 'hover',
                    container: 'body'
                })
            },
            eventClick: function(info) {
                var event = info.event;
                var title = event.title;
                var startTime = event.start;
                var endTime = event.end;
                var description = event.extendedProps.description;
                var location = event.extendedProps.location;
                var therapistId = event.extendedProps.therapistId;
                var therapist = event.extendedProps.therapist;
                var position = event.extendedProps.position;
                var profile = event.extendedProps.profile;
                var eventDate = event.start.toLocaleString('en-NZ', {year: 'numeric', month: '2-digit', day: '2-digit'});
                var eventDateParts = eventDate.split('/');
                eventDate = `${eventDateParts[2]}-${eventDateParts[1]}-${eventDateParts[0]}`;
                var classID = event.id;
                var slotsKey = `${classID}_${eventDate}`;
                var slots = classRemainSlots[slotsKey] || 15;

                // fill the modal with the event details
                document.getElementById('class-title').innerHTML = title;
                document.getElementById('class-time').innerHTML = `<strong>Time:</strong> ${combineDateTime(startTime, endTime)}`;
                document.getElementById('class-location').innerHTML = `<strong>Location:</strong> ${location}`;
                document.getElementById('class-remaining-slots').innerHTML = `<strong>Slots:</strong> ${slots} remaining`;
                document.getElementById('class-therapist').innerHTML = `<strong>Therapist:</strong> ${therapist}`
                document.getElementById('class-description').innerHTML = `<strong>Description:</strong> ${description}`
                document.getElementById('class-therapistPosition').innerHTML = `<strong>Position:</strong> ${position}`
                document.getElementById('class-therapistProfile').innerHTML = `<strong>Profile:</strong> ${profile}`
                var classDateInput = document.getElementById('class_date')
                var classIDInput = document.getElementById('class_id')
                var bookBtn = document.getElementById("book-btn")
                if (classIDInput) {
                    classIDInput.value = classID;
                }
                if (classDateInput) {
                    classDateInput.value = eventDate;
                }
                if (bookBtn) {
                    if (slots == 0) {
                        bookBtn.disabled = true;
                        bookBtn.classList.add("btn-danger");
                        bookBtn.innerHTML = "Fully Booked";
                    } else {
                        bookBtn.disabled = false;
                        bookBtn.classList.remove("btn-danger");
                        bookBtn.innerHTML = "Book Now";
                    }
                }

                // show the modal
                var classDetailModal = new bootstrap.Modal(document.getElementById('classDetailModal'))
                classDetailModal.show();
            }
        });
    }
    calendar.removeAllEvents();
    classes.forEach(event => calendar.addEvent(event))
    calendar.render();
}

// Helper functon to convert days of the week from a set to FullCalendar format
function convertDaysOfWeek(days) {
    var daysMap = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 0
    };
    return Array.from(days).map(day => daysMap[day]);
}

// Helper function to convert time to normal time format
function formatDateTime(time) {
    const formatter = new Intl.DateTimeFormat('en-NZ', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
    return formatter.format(time);
}

// Helper function to combine date and time
function combineDateTime(start, end){
    var formatStart = formatDateTime(start)
    var formatEnd = formatDateTime(end)
    var endTime = formatEnd.replace(' at ', ',').split(',')[2]
    return `${formatStart} - ${endTime}`

}