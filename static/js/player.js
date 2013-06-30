$(function() {

    var WEB_SOCKET_SWF_LOCATION = '/static/js/socketio/WebSocketMain.swf',
        socket = io.connect('/player');

    socket.on('song_changed', song_changed);

    function song_changed (msg) {
        $("#current_playing_song").text(msg)
    }

    $(function () {
        
    });

});