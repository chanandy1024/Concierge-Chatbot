var checkout = {};
var user_id;

$(document).ready(function() {
  var $messages = $('.messages-content');
  $(window).load(function() {
    $messages.mCustomScrollbar();
  })
  console.log($messages);
  var d, h, m,
  i = 0;
  user_id = localStorage.getItem('userId');
  if (user_id) {
    //search dynamodb
    //get request to API gateway and retrieve most recent search
    sdk.chatbotGet({
      user_id : user_id
    }, {}).then(data => {
      var searchResults = JSON.parse(data.data.search_results);

      $(window).load(function() {
        insertResponseMessage('Welcome back! These are your most recent recommendations:');
        for (let i = 0; i < searchResults.length; i++){
          insertResponseMessage(`${i+1}. ${searchResults[i].name}, located at ${searchResults[i].location.display_address.join(', ')}.`);
        }
        //insertResponseMessage('...or would you like new suggestions?');
      });
      // based on user_id
    }).catch(err => {
        console.log(err);
        localStorage.removeItem('userId');
        if (!user_id){
          user_id = Date.now().toString(36) + Math.random().toString(36).substring(2);
          if (!localStorage.getItem('userId')) localStorage.setItem('userId', user_id);
        }
        insertResponseMessage('Hi there, I\'m your personal Concierge. How can I help?');
    })
    //... or would you like new suggestions?
  } else {
    $(window).load(function() {
      if (!user_id){
        user_id = Date.now().toString(36) + Math.random().toString(36).substring(2);
        if (!localStorage.getItem('userId')) localStorage.setItem('userId', user_id);
      }
      insertResponseMessage('Hi there, I\'m your personal Concierge. How can I help?');
    });
  }

  function updateScrollbar() {
    console.log('update scrollbar');
    $messages.mCustomScrollbar("update");
    setTimeout(function(){
      $messages.mCustomScrollbar("scrollTo","bottom");
    },1000);
  }

  function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
      m = d.getMinutes();
      $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
  }

  function callChatbotApi(message, user_id='') {
    // params, body, additionalParams
    return sdk.chatbotPost({}, {
      messages: [{
        type: 'unstructured',
        unstructured: {
          text: message,
          user_id : user_id
        }
      }]
    }, {});

   
  }
  
  function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
      return false;
    }
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();
    
    callChatbotApi(msg, user_id=user_id)
      .then((response) => {
        var data = response.data;

        if (data.messages && data.messages.length > 0) {
          console.log('received ' + data.messages.length + ' messages');

          var messages = data.messages;

          for (var message of messages) {
            if (message.type === 'unstructured') {
              insertResponseMessage(message.unstructured.text);
            } else if (message.type === 'structured' && message.structured.type === 'product') {
              var html = '';

              insertResponseMessage(message.structured.text);

              setTimeout(function() {
                html = '<img src="' + message.structured.payload.imageUrl + '" witdth="200" height="240" class="thumbnail" /><b>' +
                  message.structured.payload.name + '<br>$' +
                  message.structured.payload.price +
                  '</b><br><a href="#" onclick="' + message.structured.payload.clickAction + '()">' +
                  message.structured.payload.buttonLabel + '</a>';
                insertResponseMessage(html);
              }, 1100);
            } else {
              console.log('not implemented');
            }
          }
        } else {
          insertResponseMessage('Oops, something went wrong. Please try again.');
        }
      })
      .catch((error) => {
        console.log('an error occurred', error);
        insertResponseMessage('Oops, something went wrong. Please try again.');
      });
  }

  $('.message-submit').click(function() {
    insertMessage();
  });

  $(window).on('keydown', function(e) {
    if (e.which == 13) {
      insertMessage();
      return false;
    }
  })

  function insertResponseMessage(content) {
    $('<div class="message loading new"><figure class="avatar"><img src="https://image.emojipng.com/79/10468079.jpg" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
      $('.message.loading').remove();
      $('<div class="message new"><figure class="avatar"><img src="https://image.emojipng.com/79/10468079.jpg" /></figure>' + content + '</div>').appendTo($('.mCSB_container')).addClass('new');
      setDate();
      updateScrollbar();
      i++;
    }, 500);
  }

});
