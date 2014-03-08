//////////////////////////////////////////////////////////////////////////
// Home
function main() {
    $(".hdr input").focus();
    $("img.btn_search").css("cursor", "pointer").click(function() { do_search(); });
    $(window).keydown(function(e) {
        if (e.which == 13) { do_search(); }
    })

    // add bookmark
    $("img.btn_add").css("cursor", "pointer").click(function() {
        var $dia = $("<div class='title'>Add bookmark</div>" +
                     "<form id='bookmark_add' action='' method='post'>" +
                     "<table><tbody>" +
                     "<tr><td>Title:</td><td><input type='text' name='title' size='40'/></td></tr>" +
                     "<tr><td>URL:</td><td><input type='text' name='url' size='40'/></td></tr>" +
                     "<tr><td>Tags:</td><td><input type='text' name='tags' size='40'/></td></tr>" +
                     "</tbody></table>" +
                     "<br/>" +
                     "<span class='comment'>Type the new information for the bookmark</span>" +
                     "<hr/>" +
                     "<div class='btns'>" +
                     "<input type='submit' name='add_bm' value='Add'/>" +
                     "<input type='submit' name='cancel' value='Cancel'/>" +
                     "</div>" +
                     "</form>").modaldialog().attr("title", "Add bookmark");
        $dia.find("input[name='add_bm']").click(function() {
            var title = $("#dialog input[name='title']").val().trim();
            var url = $("#dialog input[name='url']").val().trim();
            var tags = $("#dialog input[name='tags']").val().trim();
            if (title == '' || url == '') {
                $.modaldialog.error($dia, 'Title or URL can\'t be void');
                return false;
            }
            $.modaldialog.end($dia);
            $.post("/ajax/add", {"title": title, "url": url, "tags": tags})
                .done(function() {
                    document.location = "/";
                })
                .fail(function() {
                    alert('ERROR adding bookmark!')
                });
            return false;
        });
    });
}


function do_search() {
    text = $(".hdr input").val().trim() || "|none|";
    document.location = '/search/' + text;
}


//////////////////////////////////////////////////////////////////////////
// Bookmarks
function show_bookmarks() {
    // search boxes
    $("input.sterm").hide();
    $("span.sterm").click(function() {
        $(this).hide()
        var text = $(this).text()=='none' ? '' : $(this).text();
        $("input.sterm").show().focus().val(text);
        $("input.sterm").keyup(function(e) {
            if (e.which == 27) {
                $(this).hide();
                $("span.sterm").show();
            } else if (e.which == 13) {
                text = $("input.sterm").val().trim() || "|none|";
                document.location = '/search/' + text;
            }
        });
    });

    // bookmarks buttons
    $("ul .btns").hide();
    $("li.bookmark").hover(
        function() {
            $(this).find(".btns").show();
        }, function() {
            $(this).find(".btns").hide();
        });

    // edit bookmark
    $("li.bookmark img.btn_edit").css("cursor", "pointer").click(function() {
        var $li = $(this).parent().parent();
        var title0 = $li.find(".title").text();
        var url0 = $li.find(".url").attr("href");
        var tags0 = $li.find(".tags").text();
        var $dia = $("<div class='title'>Edit bookmark</div>" +
                     "<form id='bookmark_edit' action='' method='post'>" +
                     "<table><tbody>" +
                     "<tr><td>Title:</td><td><input type='text' name='title' value='" + title0 + "' size='40'/></td></tr>" +
                     "<tr><td>URL:</td><td><input type='text' name='url' value='" + url0 + "' size='40'/></td></tr>" +
                     "<tr><td>Tags:</td><td><input type='text' name='tags' value='" + tags0 + "' size='40'/></td></tr>" +
                     "</tbody></table>" +
                     "<br/>" +
                     "<span class='comment'>Type the new information for the bookmark</span>" +
                     "<hr/>" +
                     "<div class='btns'>" +
                     "<input type='submit' name='edit_bm' value='Edit'/>" +
                     "<input type='submit' name='cancel' value='Cancel'/>" +
                     "</div>" +
                     "</form>").modaldialog().attr("title", "Edit bookmark");
        $dia.find("input[name='edit_bm']").click(function() {
            var title = $("#dialog input[name='title']").val().trim();
            var url = $("#dialog input[name='url']").val().trim();
            var tags = $("#dialog input[name='tags']").val().trim();
            if (title == '' || url == '') {
                $.modaldialog.error($dia, 'Title or URL can\'t be void');
                return false;
            }
            $.modaldialog.end($dia);
            if (title == title0 && url == url0 && tags == tags0) {
                return false
            }
            $.post("/ajax/edit", {"url_old": url0, "title": title, "url": url, "tags": tags})
                .done(function() {
                    $li.find(".title").text(title);
                    $li.find(".url").attr("href", url).text(url);
                    var ltags = new Array();
                    $.each(tags.split(","), function(i, tag) {
                        var tag = tag.trim();
                        ltags.push("<a href='/search/|void|/" + tag + "' class='tag'>" + tag + "</a>");
                    });
                    $li.find(".tags").html(ltags.join(', '));
                })
                .fail(function() {
                    alert('ERROR editing bookmark!')
                });
            return false;
        });
    });

    // delete bookmark
    $("li.bookmark img.btn_remove").css("cursor", "pointer").click(function() {
        var $li = $(this).parent().parent();
        var title = $li.find(".title").text();
        if (confirm("Do you want to remove this bookmark from the database?\nTitle: " + title)) {
            var url = $li.find(".url").attr("href");
            $.post("/ajax/remove", {"url": url})
                .done(function(r) {
                    $li.remove();
                    $(".nbookmarks").text(parseInt($(".nbookmarks").text()-1));
                })
                .fail(function() {
                    alert("ERROR removing bookmark!\nTitle: " + title + "\nURL: " + url);
            });
        }
    });
}


//////////////////////////////////////////////////////////////////////////
// My own modal dialog
(function($) {
    // modal dialog for forms
    $.fn.modaldialog = function() {
        var doch = $(document).height(),
        winh = $(window).height(),
        winw = $(window).width();
        var $dialog = $("#dialog").empty();
        var $overlay = $("#overlay")
            .css({'top': 0, 'left': 0, 'height': doch, 'width': winw, 'opacity': 0})
            .show().animate({'opacity': 0.8});
        $(this).appendTo($dialog);
        $("#page").css({"opacity": 0.4});
        // calc size and pos, add and display dialog
        var w = $dialog.width(),
        h = $dialog.height(),
        top = winh/2 - Math.floor(h/2) + 'px',
        left = winw/2 - Math.floor(w/2) + 'px';
        $dialog
            .fadeIn()
            .css('top', top).css('left', left)
            .keydown(function(e) { e.stopPropagation(); })
            .find("input:first").focus();
        $dialog.find("input[name='cancel']").click(function() {
            $dialog.fadeOut();
            $overlay.hide();
            $("#page").css({"opacity": 1});
            return false;
        });
        return $dialog;
    };
    $.modaldialog = $.modaldialog || {};
    $.modaldialog.error = function($obj, msg) {
        $obj.find("div.dlgerr").remove();
        $("<div class='dlgerr'><img src='/img/error.png'/>&nbsp;&nbsp;" + msg + "</div>")
            .insertBefore($obj.find("form table"));
        $obj.find("input:first").focus();
    };
    $.modaldialog.end = function($obj) {
        $obj.fadeOut();
        $("#overlay").hide();
        $("#page").css({"opacity": 1});
    };
})(jQuery);


//////////////////////////////////////////////////////////////////////////
