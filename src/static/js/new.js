let numberOfChoices = 0;
let question = 1;

let questionList = [];

/*
 * Will clear all values in the multiple choice creation form.
 */
function clearFormsMC() {
    document.getElementById('mcname').value = "";
    document.getElementById('choice1').value = "";
    document.getElementById('choice2').value = "";
    document.getElementById('choice3').value = "";
    document.getElementById('choice4').value = "";
    document.getElementById('choice5').value = "";
}

/*
 * Will clear all values in the rating scale creation form.
 */
function clearFormsRS() {
    document.getElementById('rsname').value = "";
    document.getElementById('scale1').value = "";
    document.getElementById('scale10').value = "";
}

/*
 * Will clear all values in the short answer creation form.
 */
function clearFormsSA() {
    document.getElementById('saname').value = "";
}

function addRowMC() {
    // get question from the question input
    var fname = document.getElementById('mcname').value;

    // get the html table
    // 0 = the first table
    var table = document.getElementsByTagName('table')[0];

    // add new empty row to the table
    // 0 = in the top 
    // table.rows.length = the end
    // table.rows.length/2+1 = the center
    var questionRow = table.insertRow(table.rows.length);
    var choiceRow = table.insertRow(table.rows.length);

    questionRow.setAttribute('class', 'questionMC');
    choiceRow.setAttribute('class', 'choicesRadio');

    // add cells to the row
    var cel1 = questionRow.insertCell(0);
    cel1.innerHTML = `Question ${question}: ` + fname;
    question++;

    for (let i = numberOfChoices; i >= 1; --i) {
        let isCheckBox = document.getElementById('turnCheckbox').checked;
        let choice = document.getElementById(`choice${i}`).value;
        let newDiv;
        if (isCheckBox) {
            newDiv = (`<input type="checkbox" name="inlineCheckboxOptions" id="inlineCheckbox${i}" value="${i}"> ${choice}`);
        }
        else {
            newDiv = (`<input type="radio" name="inlineRadioOptions" id="inlineRadio${i}" value="${i}"> ${choice}`);
        }
        var newCel = choiceRow.insertCell(0);
        newCel.innerHTML = newDiv;
    }

    clearFormsMC();
    mcDisplay();
}

function addRowRS() {
    // get question from the question input
    var fname = document.getElementById('rsname').value;
    var newDiv = ('<div class="btn-group btn-group-lg"><button type="button" class="btn btn-secondary">1</button><button type="button" class="btn btn-secondary">2</button><button type="button" class="btn btn-secondary">3</button><button type="button" class="btn btn-secondary">4</button><button type="button" class="btn btn-secondary">5</button><button type="button" class="btn btn-secondary">6</button><button type="button" class="btn btn-secondary">7</button><button type="button" class="btn btn-secondary">8</button><button type="button" class="btn btn-secondary">9</button><button type="button" class="btn btn-secondary">10</button></div>');

    var scaleAt1 = document.getElementById('scale1').value;
    var scaleAt10 = document.getElementById('scale10').value;
    // get the html table
    // 0 = the first table
    var table = document.getElementsByTagName('table')[0];

    // add new empty row to the table
    // 0 = in the top 
    // table.rows.length = the end
    // table.rows.length/2+1 = the center
    var questionRow = table.insertRow(table.rows.length);
    var scaleRow = table.insertRow(table.rows.length);
    //var choiceRow = table.insertRow(table.rows.length);

    questionRow.setAttribute('class', 'questionMC');
    scaleRow.setAttribute('class', 'scaleRow');
    //choiceRow.setAttribute('class', 'choicesScale');

    // add cells to the row
    var cel1 = questionRow.insertCell(0);
    cel1.innerHTML = `Question ${question}: ` + fname + ` (Scale: 1 = ${scaleAt1}` + " and " + `10 = ${scaleAt10})`;
    question++;

    var cel2 = scaleRow.insertCell(0);

    cel2.innerHTML = newDiv;

    clearFormsRS();
    rsDisplay();
}

function addRowSA() {
    // get question from the question input
    var fname = document.getElementById('saname').value;
    var newDiv = ('<textarea class="form-control z-depth-1" rows="3" placeholder="Enter your response here!"></textarea>');

    // get the html table
    // 0 = the first table
    var table = document.getElementsByTagName('table')[0];

    // add new empty row to the table
    // 0 = in the top 
    // table.rows.length = the end
    // table.rows.length/2+1 = the center
    var questionRow = table.insertRow(table.rows.length);
    var textAreaRow = table.insertRow(table.rows.length);

    questionRow.setAttribute('class', 'questionMC');
    textAreaRow.setAttribute('class', 'myTextArea');

    // add cells to the row
    var cel1 = questionRow.insertCell(0);
    cel1.innerHTML = `Question ${question}: ` + fname;
    question++;

    var cel2 = textAreaRow.insertCell(0);

    cel2.innerHTML = newDiv;

    clearFormsSA();
    shortDisplay();
}
function disableFunction(choiceString) {
    let myValue = document.getElementById(`${choiceString}`).value;
    for (let i = 1; i <= 5; ++i) {
        if (i <= myValue) {
            document.getElementById(`choice${i}`).disabled = false;
        }
        else {
            document.getElementById(`choice${i}`).disabled = true;
            document.getElementById(`choice${i}`).value = "";
        }
    }        
    numberOfChoices = myValue;
}
function mcDisplay() {
    var current = document.getElementById('multipleChoice');
    var ratingScaleDisplay = document.getElementById('ratingScale');
    var shortAnswerDisplay = document.getElementById('shortAnswer');
    if (current.style.display === 'none') {
        current.style.display = 'block';
        ratingScaleDisplay.style.display = 'none';
        shortAnswerDisplay.style.display = 'none';
    }
}
function rsDisplay() {
    var multipleChoice = document.getElementById('multipleChoice');
    var current = document.getElementById('ratingScale');
    var shortAnswerDisplay = document.getElementById('shortAnswer');
    if (current.style.display === 'none') {
        current.style.display = 'block';
        multipleChoice.style.display = 'none';
        shortAnswerDisplay.style.display = 'none';
    }
}
function shortDisplay() {
    var multipleChoice = document.getElementById('multipleChoice');
    var ratingScaleDisplay = document.getElementById('ratingScale');
    var current = document.getElementById('shortAnswer');
    if (current.style.display === 'none') {
        current.style.display = 'block';
        ratingScaleDisplay.style.display = 'none';
        multipleChoice.style.display = 'none';
    }
}