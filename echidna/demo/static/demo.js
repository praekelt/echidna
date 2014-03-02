(function () {
    var self = this;

    self.ws = null;

    self.init = function () {
        self.ws.init();
        self.pub.init();
        self.recv.init();
    };


    self.pub = {};
    self.pub.btn = null;
    self.pub.text = null;

    self.pub.init = function () {
        self.pub.btn = $("#publish-form .echidna-publish-btn");
        self.pub.text = $("#publish-form .echidna-publish-text");
        self.pub.btn.on("click", self.pub.on_publish);
    };

    self.pub.on_publish = function () {
        var text = self.pub.text.val().trim(),
            msg = null;

        if (text) {
            msg = {
                created: $.now(),
                text: text,
            }
            self.ws.send_msg(msg);
            self.debug("Published: " + JSON.stringify(msg));
        }

        self.pub.text.val("");
    };


    self.recv = {};
    self.recv.msg_list = null;
    self.recv.msgs = null;

    self.recv.init = function () {
        self.recv.msg_list = $("#received-list");
        self.recv.msgs = [];
    };

    self.recv.on_msg = function (msg) {
        if (self.recv.msgs.length == 0) {
            self.recv.msg_list.empty();
        }
        self.recv.msgs.push(msg);
        var created = moment(msg.created).format("MMMM Do YYYY, h:mm:ss a");
        self.recv.msg_list.prepend(
            '<li class="list-group-item">' +
                '<span class="badge">' + created + '</span>' +
                msg.text +
            '</li>'
        );
    };

    self.ws = {};
    self.ws.server = null;

    self.ws.init = function () {
        var server = new WebSocket("ws://localhost:8888/subscribe");
        self.ws.server = server;
        server.onopen = self.ws.on_open;
        server.onclose = self.ws.on_close;
        server.onmessage = self.ws.on_message;
        server.onerror = self.ws.on_error;
    };

    self.ws.send_msg = function (msg) {
        self.ws.server.send(JSON.stringify(msg));
    };

    self.ws.on_open = function () {
        self.debug("connected");
    };

    self.ws.on_close = function () {
        self.debug("connected");
    };

    self.ws.on_message = function (event) {
        self.debug("received: " + event.data);
        var msg = JSON.parse(event.data);
        self.recv.on_msg(msg);
    };

    self.ws.on_error = function (e) {
        self.debug(e);
    };

    self.debug = function (d) {
        console.log("DEBUG: " + d);
    };

    $(document).ready(self.init);
})();