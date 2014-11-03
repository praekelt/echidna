(function (exports) {


    function debug (d) {
        console.log("DEBUG: " + d);
    };


    function EchidnaPublisher ($publish_form, api_server) {
        var self = this;

        self.api_server = api_server;
        self.$publish_form = $publish_form;

        self.init = function () {
            var btn = self.$publish_form.find(".echidna-publish-btn");
            btn.on("click", self.on_publish);
        };

        self.post = function (channel, msg) {
            debug("Publishing to " + channel + " ...");
            debug(JSON.stringify(msg));

            var xhdr = $.post(
                "http://" + self.api_server + "/publish/" + channel + "/",
                JSON.stringify(msg)
            ).done(function (data, status) {
                debug("Published successfully.");
            }).fail(function () {
                debug("Publishing failed. :/");
            });
        };

        self.on_publish = function () {
            var text_input = self.$publish_form.find(".echidna-publish-text");
            var channel_input = self.$publish_form.find(
                ".echidna-publish-channels :checked");

            var text = text_input.val().trim(),
                channel = channel_input.val().trim(),
                msg = null;

            if (text) {
                msg = {
                    publish_on: $.now() / 1000,
                    title: text,
                }
                self.post(channel, msg);
            }

            text_input.val("");
        };

        self.init();
    }


    function EchidnaApi (api_server, opts) {
        var self = this;

        self.api_server = api_server;
        self.callbacks = opts.callbacks || {};

        self.socket = null;

        self.init = function () {
            var socket = new WebSocket("ws://" + self.api_server + "/subscribe");
            self.socket = socket;
            socket.onopen = self.ws.on_open;
            socket.onclose = self.ws.on_close;
            socket.onmessage = self.ws.on_message;
            socket.onerror = self.ws.on_error;
        };

        self.callback = function () {
            var name = Array.prototype.shift.call(arguments);
            if (self.callbacks[name]) {
                self.callbacks[name].apply(self, arguments);
            };
        };

        self.ws = {};

        self.ws.on_open = function () {
            debug("connected");
            self.callback('on_open');
        };

        self.ws.on_close = function () {
            debug("disconnected");
            self.callback('on_close');
        };

        self.ws.on_message = function (event) {
            debug("received: " + event.data);
            var msg = JSON.parse(event.data);
            var callback_name = "handle_" + msg.msg_type;
            self.callback(callback_name, msg);
        };

        self.ws.on_error = function (e) {
            debug(e);
            self.callback('on_error', e);
        };

        self.send_msg = function (msg) {
            self.socket.send(JSON.stringify(msg));
        };

        self.subscribe = function (channel) {
            self.send_msg({
                "msg_type": "subscribe",
                "channel": channel,
            });
        };

        self.unsubscribe = function (channel) {
            self.send_msg({
                "msg_type": "unsubscribe",
                "channel": channel,
            });
        };

        self.init();
    }


    function EchidnaReceiver ($receive_form, $msg_list, api_server) {
        var self = this;

        self.$receive_form = $receive_form;
        self.$channel_boxes = $receive_form.find("input[type=checkbox]");
        self.$msg_list = $msg_list;
        self.$no_cards_li = $msg_list.find(".echidna-no-cards");
        self.api_server = api_server;

        self.api = null;
        self.channels = {};

        self.init = function () {
            self.api = new EchidnaApi(self.api_server, {
                "callbacks": {
                    "on_open": self.on_open,
                    "handle_card": self.handle_card,
                    "handle_error": self.handle_error
                }
            });
            self.$channel_boxes.on("click", self.update_channels);
        };

        self.update_channels = function () {
            self.$channel_boxes.each(function (idx, elem) {
                var channel = elem.value;
                if (elem.checked && !self.channels[channel]) {
                    self.add_channel(channel);
                }
                else if (!elem.checked && self.channels[channel]) {
                    self.remove_channel(channel);
                }
            });
        };

        self.add_channel = function (channel) {
            debug("Adding channel " + channel + " ...");
            self.channels[channel] = true;
            self.api.subscribe(channel);
        };

        self.remove_channel = function (channel) {
            debug("Removing channel " + channel + " ...");
            self.channels[channel] = false;
            self.api.unsubscribe(channel);
            self.remove_channel_msgs(channel);
        };

        self.remove_channel_msgs = function (channel) {
            self.$msg_list.find("li[channel='" + channel + "']").remove();
            self.check_no_cards_li();
        };

        self.check_msg_overflow = function () {
            self.$msg_list.find("li:visible:gt(20)").remove();
        };

        self.check_no_cards_li = function () {
            msg_count = self.$msg_list.find("li:visible").length;
            debug(msg_count);
            if (msg_count == 0) {
                self.$no_cards_li.show();
            }
            else if (msg_count > 1) {
                self.$no_cards_li.hide();
            }
        };

        self.on_open = function () {
            self.update_channels();
        };

        self.handle_card = function (msg) {
            var card = msg.card;
            var channel = msg.channel;
            // Convert timestamp to miliseconds
            var publish_on = moment(card.publish_on * 1000).format("MMMM Do YYYY, h:mm:ss a");
            self.$msg_list.prepend(
                '<li class="list-group-item" channel="' + channel + '">' +
                    '<span class="badge">' + publish_on + '</span>' +
                    '<span class="badge channel">' + channel + '</span>' +
                    card.title +
                    '</li>'
            );
            self.check_msg_overflow();
            self.check_no_cards_li();
        };

        self.handle_error = function (msg) {
            debug("ERROR msg: " + JSON.stringify(msg));
        };

        self.init();
    }

    exports.EchidnaPublisher = EchidnaPublisher;
    exports.EchidnaApi = EchidnaApi;
    exports.EchidnaReceiver = EchidnaReceiver;

})(window.echidna = window.echidna || {});
