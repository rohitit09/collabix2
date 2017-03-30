(function () {
    var Message;
    Message = function (arg) {
        this.text = arg.text, this.message_side = arg.message_side;
        this.draw = function (_this) {
            return function () {
                var $message;
                $message = $($('.message_template').clone().html());
                $message.addClass(_this.message_side).find('.text').html(_this.text);
                $('.messages').append($message);
                return setTimeout(function () {
                    return $message.addClass('appeared');
                }, 0);
            };
        }(this);
        return this;
    };
    $(function () {
        var getMessageText, message_side, sendMessage;
        message_side = 'right';
        getMessageText = function () {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };
        sendMessage = function (text) {
            var $messages, message;
            if (text.trim() === '') {
                return;
            }
            $('.message_input').val('');
            $messages = $('.messages');
            message_side = message_side === 'left' ? 'right' : 'left';
            message = new Message({
                text: text,
                message_side: message_side
            });
            message.draw();
            return $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
        };
        getResponseFromServer= function(name) {

        };
        compareStrings = function(string1, string2) {
            string1 = string1.toLowerCase();
            string2 = string2.toLowerCase();
            return string1 === string2;
        };
        fetchData = function() {
            var form = new FormData();
            form.append('name', 'Person name');
            form.append('dob', '23/23/2034');

            fetch('http://127.0.0.1:5000/getDetails', {
                method: 'post',
                body: form,
                mode: 'no-cors',
                headers: {
                    Accept: 'application/json',
                }
            }).then(function(response) {
                console.log(response);
            }).catch(function(err){
                console.log(err);
            });
        };
        processInput = function(input) {
            console.log(compareStrings(input, 'hi'));
            if (compareStrings(input, 'Hi')) {
                return 'Do you want to go for claim or renewal?';
            } else if (compareStrings(input, 'claim')){
                return "Have you already submitted the claim form?";
            } else if (compareStrings(input, 'yes')){
                // fetchData();
                // hit web service
                return "Congrats, You will get the money soon.";
            } else if (compareStrings(input, 'no')) {
                // dfdf
                return "So you know the next step.";
            } else if(compareStrings(input, 'Renewal')) {
                setTimeout(sendMessage.bind(this, "You have to pay the premium of Rs.34295"), 3000);
                return "Please enter your policy number and birthdate";
                // hit webservice
            }
        };
        $('.send_message').click(function (e) {
            var data = $('.message_input').val();
            console.log("data", data);

            $.ajax({
                  type: 'POST',
                  contentType: 'application/json',
                  url: 'http://localhost:5000/matchquestion',
                  dataType : 'json',
                  data : JSON.stringify(data),
                  success : function(result) {
                      console.log("result -->", result);
                      
                  },error : function(err){
                    alert("Something is wrong", err)
                     console.log(result);
                  }
              });

        });
        $('.message_input').keyup(function (e) {
            if (e.which === 13) {
                // sendMessage(processInput(getMessageText()));
                setTimeout(sendMessage.bind(this, processInput(getMessageText())), 200);
                return sendMessage(getMessageText());
            }
        });
        // sendMessage('Hello Philip! :)');
        // setTimeout(function () {
        //     return sendMessage('Hi Sandy! How are you?');
        // }, 1000);
        // return setTimeout(function () {
        //     return sendMessage('I\'m fine, thank you!');
        // }, 2000);
    });
}.call(this));