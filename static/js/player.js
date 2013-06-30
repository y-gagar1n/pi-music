$(function() {

    var WEB_SOCKET_SWF_LOCATION = '/static/js/socketio/WebSocketMain.swf',
        socket = io.connect('/player');

    socket.on('song_changed', song_changed);
    socket.on('playlist_updated', playlist_updated);

    function song_changed (msg) {
        $("#current_playing_song").text(msg);
        update_playlist();
    }

    function playlist_updated(msg) {
    	update_playlist();
    }

    $(function () {
    });

});

function update_playlist()
{
  $.ajax({
    type: "GET",
    contentType: "application/json; charset=utf-8",
    url: "/playlist",
    success: function(response)
    {
		$("#playlist_placeholder").html(response);
    }
  });
}

function ajax_call(url)
{
  $.ajax({
    type: "GET",
    contentType: "application/json; charset=utf-8",
    url: url
  });
}

function render_partial(url)
{
  $.ajax({
    type: "GET",
    contentType: "application/json; charset=utf-8",
    url: url,
    success:function(result) {
      $("#partial_body").html(result)
    }
  });
}