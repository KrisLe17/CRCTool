// Input validation for form. Require server names in the input box or a csv file
const nameBox = document.getElementById("host-names");
const fileBox = document.getElementById("file-upload");
const maintDate = document.getElementById("maintDate");
const maintTime = document.getElementById("maintTime");
const duration = document.getElementById("duration");

document.getElementById("file-selected").innerHTML = "No File Selected";

nameBox.required = true;
fileBox.required = true;

nameBox.addEventListener("input", function(){
    toggleRequired(nameBox);
});

fileBox.addEventListener("input", function(){
    toggleRequired(fileBox);
});


// if we entered host names in the box, we don't need a file and vice versa
function toggleRequired(info_entered){
    if (info_entered == nameBox){
        fileBox.required = false;
    } else if (info_entered == fileBox) {
        nameBox.required = false;
    }
}

// Show loading message/gif when form is submitted
// onclick bypasses the form validation stage so we have to make sure stuff is entered here before loading...
function loading(){
    if (validate_hosts() && validate_date() && validate_duration() && validate_time()){
        document.querySelector("#loading").style.display = "flex";
        document.querySelector("#content").style.display = "none";
    }
}

function validate_hosts(){
    if (nameBox.value != ""){
        return true;
    }
    if (fileBox.value != ""){
        var extension = fileBox.value.split('.')[1]
            if (extension == "csv" || extension == "xls" || extension == "xlsx"){
                return true;
            }
    }
    return false;
}

function validate_date(){
    const date = new Date();
    const maint_date = addDays(maintDate.value, 1);
    if (maintDate.value.length != 0 && maint_date >= date){
        return true;
    }
    return false;
}

function addDays(date, days){
    var adjusted = date + "T20:00:00-04:00" 
    var result = new Date(adjusted);
    result.setDate(result.getDate() + days);
    return result;
}

function validate_duration(){
    if (duration.value > 0 && duration.value % 1 == 0){
        return true;
    }
    return false;
}

function validate_time(){
    if (maintTime.value.length != 0){
        return true;
    }
    return false;
}

// display file name once a file is chosen
 fileBox.onchange = function(){
    var fileName = '';
    fileName = this.value;
    fileName = fileName.split('\\').pop();
    document.getElementById("file-selected").innerHTML = fileName;
 }