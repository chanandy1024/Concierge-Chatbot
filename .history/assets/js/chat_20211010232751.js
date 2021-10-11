var checkout = {};
var user_id;

$(document).ready(function() {
  var $messages = $('.messages-content'),
  d, h, m,
  i = 0;
  user_id = localStorage.getItem('userId');
  if (user_id) {
    //search dynamodb
    //get request to API gateway and retrieve most recent search
    sdk.chatbotGet({
      user_id : user_id
    }, {}).then(data => {
      console.log(data);
      var searchResults = JSON.parse(data.data.search_results);
      console.log(searchResults);
      // based on user_id
      $(window).load(function() {
        $messages.mCustomScrollbar();
        insertResponseMessage('Welcome back! These are your most recent recommendations:');
        insertResponseMessage(``);
      });
    }).catch(err => {
        console.log(err);
        $(window).load(function() {
          $messages.mCustomScrollbar();
          insertResponseMessage('Hi there, I\'m your personal Concierge. How can I help?');
        });
    })
    //... or would you like new suggestions?
  } else {
    $(window).load(function() {
      $messages.mCustomScrollbar();
      insertResponseMessage('Hi there, I\'m your personal Concierge. How can I help?');
    });
  }

  function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
      scrollInertia: 10,
      timeout: 0
    });
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
    
    if (!user_id){
      user_id = Date.now().toString(36) + Math.random().toString(36).substring(2);
      if (!localStorage.getItem('userId')) localStorage.setItem('userId', user_id);
    }
    callChatbotApi(msg, user_id=user_id)
      .then((response) => {
        console.log(response);
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
    $('<div class="message loading new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
      $('.message.loading').remove();
      $('<div class="message new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure>' + content + '</div>').appendTo($('.mCSB_container')).addClass('new');
      setDate();
      updateScrollbar();
      i++;
    }, 500);
  }

});
