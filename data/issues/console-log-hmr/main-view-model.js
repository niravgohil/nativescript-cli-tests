var Observable = require("tns-core-modules/data/observable").Observable;

function getMessage(counter) {
    if (counter <= 0) {
        return "Hoorraaay! You unlocked the NativeScript clicker achievement!";
    } else {
        return counter + " taps left";
    }
}

function createViewModel() {
    var viewModel = new Observable();
    viewModel.counter = 42;
    viewModel.message = getMessage(viewModel.counter);
    console.log("LOG Hello");

    viewModel.onTap = function() {
        this.counter--;
        this.set("message", getMessage(this.counter));
    }

    return viewModel;
}

exports.createViewModel = createViewModel;