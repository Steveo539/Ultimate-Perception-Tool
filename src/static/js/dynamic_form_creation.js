// Global Variables
// -----------------------
questionList = []; //Key-Value pair for questions. Key is UniqueID, Value is Question Content
addedRows = [];

//
// -----------------------
// Event Handlers For Page + Setup
// -----------------------
//

// We disable page scrolling so that the div with questions gets priority
document.body.style.overflowY = "hidden";


//
// -----------------------
// Logic For Adding/Removing Questions
// -----------------------
//

/**
 * Adds a specific multiple choice question to the list, and adds associated required values
 * such as adding the HTML element, creating the class, and adding to master list of survey fields
 */
function addQuestionMultipleChoice() {
    let formValues = formToFieldList('mcForm');
    // Will Return List with the following:
    // Index 0: Question Title
    // Index 1: Multiple Selection Allowed
    // Index 2-...: Question Values

    let mcTitle = formValues[0];
    let mcMultiple = formValues[1];
    let mcQuestions = [];

    for (let index = 2; index < formValues.length; index++) {
        mcQuestions.push(formValues[index]);
    }

    let mcQuestion = new MultipleChoiceQuestion(mcTitle, mcMultiple, mcQuestions);

    questionList.push(mcQuestion);
    addRowMultipleChoice(mcQuestion);
    clearForm('mcForm');
    $('#mcModal').modal('hide');

    for (let index = addedRows.length - 1; index >= 0; index--) { // Remove all added rows from the fields
        removeRow(addedRows[index]);
    }
}

/**
 * Adds a specific rating scale question to the list, and adds associated required values
 * such as adding the HTML element, creating the class, and adding to master list of survey fields
 */
function addQuestionRatingScale() {
    let formValues = formToFieldList('rsForm');
    // Will Return List with the following:
    // Index 0: Question Title
    // Index 1: Minimum Value
    // Index 2: Maximum Value
    // Index 3: Minimum Value Label
    // Index 4: Maximum Value Label
    let rsTitle = formValues[0];
    let rsMinV = formValues[1];
    let rsMaxV = formValues[2];
    let rsMinL = formValues[3];
    let rsMaxL = formValues[4];

    let rsQuestion = new RatingScaleQuestion(rsTitle, rsMinV, rsMaxV, rsMinL, rsMaxL);

    questionList.push(rsQuestion);
    addRowRatingScale(rsQuestion);
    clearForm('rsForm');
    $('#rsModal').modal('hide');
}


/**
 * Adds a specific short answer question to the list, and adds associated required values
 * such as adding the HTML element, creating the class, and adding to master list of survey fields
 */
function addQuestionShortAnswer() {
    let formValues = formToFieldList('saForm');
    // Will Return List with the following:
    // Index 0: Question Title

    let saTitle = formValues[0];

    let saQuestion = new ShortAnswerQuestion(saTitle);

    questionList.push(saQuestion);
    addRowShortAnswer(saQuestion);
    clearForm('saForm');
    $('#saModal').modal('hide');
}

function prepareJSON() {
    let jsonField = document.getElementById('json');

    let jsonList = questionList.map(function (question) {
        return question.toJson();
    });

    jsonField.value = JSON.stringify(jsonList);
}

//
// -----------------------
// Helper Functions
// -----------------------
//

/**
 * Given a form name, will return a javascript list of all field values
 * in the form.
 * @param formID The ID of the form in HTML
 */
function formToFieldList(formID) {
    let form = document.getElementById(formID).elements;
    let formValues = [];

    for (let i = 0; i < form.length; i++) {
        if (form[i].type === 'text') {
            formValues.push(form[i].value)
        }
        if (form[i].type === 'checkbox') {
            formValues.push(form[i].checked)
        }
    }
    return formValues;
}

/**
 * Clears all of the text fields in a form, resetting them to blank and
 * setting all true/false checkboxes to unchecked.
 * @param formID The ID of the form in HTML
 */
function clearForm(formID) {
    let form = document.getElementById(formID).elements;

    for (let i = 0; i < form.length; i++) {
        if (form[i].type === 'text') {
            form[i].value = '';
        }
        if (form[i].type === 'checkbox') {
            form[i].checked = false;
        }
    }
}

/**
 * Adds a row into the HTML file showing the multiple choice field which was created.
 */
function addRowMultipleChoice(mcQuestion) {
    const div = document.createElement('div');

    div.className = 'form';
    div.id = mcQuestion.uuid;

    let optionType = 'radio';

    if (mcQuestion.multiple) {
        optionType = 'checkbox';
    }

    let optionDisplay = ``;
    let list = mcQuestion.optionList;
    for (let index = 0; index < mcQuestion.optionList.length; index++) {
        optionDisplay += `
        <div class="` + optionType + `">
            <input name="` + div.id + index + `" id="` + div.id + index + `" type="` + optionType + `" disabled>
            <label for="` + div.id + index + `">
            ` + mcQuestion.optionList[index].toString() + `
            </label>
        </div>   
        `;
    }

    div.innerHTML = `
    <div class="card">
    <div class="card-body">
         <h5 class="card-title">` + mcQuestion.title + `</h5>
         <div>` + optionDisplay + `</div>
    </div>
        <button type="button" class="btn btn-danger bmd-btn-icon-bg" ondblclick='removeRow(\"` + div.id.toString() + `\")'>
            <i class="material-icons">delete</i>
        </button>
    </div>
    <br>
    `
    ;

    document.getElementById('questions').appendChild(div);
}

function addRowRatingScale(rsQuestion) {
    const div = document.createElement('div');

    div.className = 'form';
    div.id = rsQuestion.uuid;
    div.innerHTML = `
    <div class="lead"><b>` + rsQuestion.title + `</b>
        <button type="button" class="btn btn-danger bmd-btn-icon-sm" onclick='removeRow(\"` + div.id.toString() + `\")'>
            <i class="material-icons">delete</i>
        </button>
    </div>
    <div class="row text-center">
        <div class="col text-left">
            ` + rsQuestion.minLabel + `
        </div>
    
        <div class="col text-right">
            ` + rsQuestion.maxLabel + `
        </div>
    </div>
    <input type="range" class="custom-range" min="0" max="5" id="` + rsQuestion.uuid + 0 + `">
    `;

    document.getElementById('questions').appendChild(div);
}

/**
 * Adds a row into the HTML file showing the short answer field which was created.
 */
function addRowShortAnswer(saQuestion) {
    const div = document.createElement('div');

    div.className = 'form';
    div.id = saQuestion.uuid;
    div.innerHTML = `
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">` + saQuestion.title + `</h5>
                <form>
                    <div class="form-group">
                        <label for="area\` + div.id + \`" class="bmd-label-floating">Short Answer Response Question</label>
                    </div>
                </form>

        </div>
                <button type="button" class="btn btn-danger bmd-btn-icon-sm" ondblclick='removeRow(\"` + div.id.toString() + `\")'>
            <i class="material-icons">delete</i>
        </button>
        </div>

        <br>
`;

    document.getElementById('questions').appendChild(div);
}


/**
 * Removes a given row from the question display section.
 * @param questionID Exact object to remove
 */
function removeRow(questionID) {
    questionID = questionID.trim();
    document.getElementById(questionID).remove();

    if (questionID.length < 10) {  //If it is a short ID, we know it is an added row
        for (let i = 0; i < addedRows.length; i++) {
            if (addedRows[i] === questionID) {
                addedRows.splice(i, 1);
                break;
            }
        }
    } else { // Otherwise it is a question ID
        for (let i = 0; i < questionList.length; i++) {
            if (questionList[i].uuid === questionID) {
                questionList.splice(i, 1);
                break;
            }
        }
    }
}

/**
 * Generates a unique identifier. This is used for questions to give them a unique field value
 * that can be easily queried in the HTML.
 * @returns {string} UUID Value
 */
function generateUUID() {
    return 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        let r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * Will create a new blank input for a multiple choice field. This is required in the form, and will
 * have an associated delete button should you decide to not want the field anymore.
 */
function addBlankInput() {
    const div = document.createElement('div');

    div.className = 'row';
    div.id = generateUUID().substr(0, 9);
    div.innerHTML = `
            <div class="form-group col-8">
                <label for="` + div.id + "0" + `" class="bmd-label-static">Response Option</label>
                <input type="text" class="form-control" id="` + div.id + "0" + `" required>
            </div>
            <div class="col-4">
                <br>
                <button type="button" class="btn btn-danger bmd-btn-icon" onclick='removeRow(\"` + div.id.toString() + `\")'>
                    <i class="material-icons">delete</i>
                </button>
            </div>
        `;

    document.getElementById('mcFormBody').appendChild(div);
    addedRows.push(div.id);
}


//
// -----------------------
// Question Classes
// -----------------------
//

class MultipleChoiceQuestion {

    /**
     * Create a new MultipleChoiceQuestion Object
     * @param title Question Title: string
     * @param optionList List of question values: list
     * @param multiple: whether multiple values are allowed to be selected for an answer
     */
    constructor(title, multiple, optionList) {
        this._type = 'multiple_choice';
        this._title = title;
        this._optionList = optionList;
        this._multiple = multiple;
        this._uuid = generateUUID();
    }

    /**
     * Returns a JSON object containing all of the data in the question.
     */
    toJson() {
        return {
            type: this._type,
            title: this._title,
            multiple: this._multiple,
            optionList: this._optionList
        };
    }

    get title() {
        return this._title;
    }

    get optionList() {
        return this._optionList;
    }

    get multiple() {
        return this._multiple;
    }

    get uuid() {
        return this._uuid;
    }

    get type() {
        return this._type;
    }

}

class RatingScaleQuestion {

    /**
     * Creates a new RatingScaleQuestion Object
     * @param title Title of Question
     * @param min minimum numeric value for question
     * @param max Maximum numeric value for question
     * @param minLabel Label for minimum value (i.e. 'not satisfied')
     * @param maxLabel Label for maximal value (i.e. 'very satisfied')
     */
    constructor(title, min, max, minLabel, maxLabel) {
        this._type = 'rating_scale';
        this._title = title;
        this._minValue = min;
        this._maxValue = max;
        this._minLabel = minLabel;
        this._maxLabel = maxLabel;
        this._uuid = generateUUID();
        this._min = min;
        this._max = max;
    }

    /**
     * Returns a JSON object containing all of the data in the question.
     */
    toJson() {
        return {
            type: this._type,
            title: this._title,
            minValue: this._minValue,
            maxValue: this._maxValue,
            minLabel: this._minLabel,
            maxLabel: this._maxLabel
        };
    }

    get uuid() {
        return this._uuid;
    }

    get title() {
        return this._title;
    }

    get min() {
        return this._min;
    }

    get max() {
        return this._max;
    }

    get minLabel() {
        return this._minLabel;
    }

    get maxLabel() {
        return this._maxLabel;
    }
}


class ShortAnswerQuestion {

    /**
     * Creates a new short answer question with a given title.
     * @param title Title for short answer question
     */
    constructor(title) {
        this._type = 'short_answer';
        this._title = title;
        this._uuid = generateUUID();
    }

    /**
     * Returns a JSON object containing all of the data in the question.
     */
    toJson() {
        return {
            type: this._type,
            title: this._title,
        };
    }

    get uuid() {
        return this._uuid;
    }

    get title() {
        return this._title;
    }
}
