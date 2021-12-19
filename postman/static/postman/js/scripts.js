function toggleCheck(el) {
    let checkboxes = document.querySelectorAll('input[type="checkbox"]');
    if (el.checked) {
        for (let i=0; i < checkboxes.length; i++) {
            if (checkboxes[i].type =='checkbox') {
                checkboxes[i].checked = true;
            }
        } toggleActions(el);
    } else {
        for (let i=0; i < checkboxes.length; i++) {
            if (checkboxes[i].type == 'checkbox') {
                checkboxes[i].checked = false;
            }
        } toggleActions(el);
    }
}

function toggleActions(el) {
    let checked = false;
    let unchecked = true;
    let checkboxes = document.querySelectorAll('input[type="checkbox"]');
    let checkAllBox = document.querySelector('#checkAll');
    let dynamicCheckboxes = document.querySelectorAll('.checkbx');
    let actions = document.querySelector('.actions').children;
    if (el.checked) {
        for (let i=0; i < actions.length; i++) {
            if (actions[i].hasAttribute('disabled')) {
                actions[i].removeAttribute('disabled');
            }
        }
        // if all dynamic boxes are checked, make sure select all box gets checked.
        let j = 0;
        for (let i=0; i < dynamicCheckboxes.length; i++) {
            if (dynamicCheckboxes[i].checked) {
                j+=1;
            } 
        }
        if (j == dynamicCheckboxes.length) {
            checkAllBox.checked = true;
        }
    } else {
        // if ANY checkboxes are checked, set to true.
        for (let i=0; i < checkboxes.length; i++) {
            if (checkboxes[i].checked) {
                checked = true;
            }
        } 
        // we only want to disable actions if ALL checkboxes are false.
        if (checked == false) {
            for (let i=0; i < actions.length; i++) {
                actions[i].setAttribute('disabled', '');
            }   
        }
         // BESIDES the select all checkbox, check if any boxes are checked.
        for (let i=0; i < dynamicCheckboxes.length; i++) {
            if (dynamicCheckboxes[i].checked == false) {
                unchecked = true;
            }
        }
        // if any boxes are not checked make sure check all gets unchecked.
        if (unchecked) {
            checkAllBox.checked = false;
        }
    }
}