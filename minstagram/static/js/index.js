$(function () {
    var oExports = {
        initialize: fInitialize,
        // 渲染更多数据
        renderMore: fRenderMore,
        // 请求数据
        requestData: fRequestData,
        // 简单的模板替换
        tpl: fTpl
    };
    // 初始化页面脚本
    oExports.initialize();

    function fInitialize() {
        var that = this;
        // 常用元素
        that.listEl = $('div.js-image-list');
        // 初始化数据
        that.uid = window.uid;
        that.page = 1;
        that.pageSize = 5;
        that.listHasNext = true;
        // 绑定事件
        $('.js-load-more').on('click', function (oEvent) {
            var oEl = $(oEvent.currentTarget);
            var sAttName = 'data-load';
            // 正在请求数据中，忽略点击事件
            if (oEl.attr(sAttName) === '1') {
                return;
            }
            // 增加标记，避免请求过程中的频繁点击
            oEl.attr(sAttName, '1');
            that.renderMore(function () {
                // 取消点击标记位，可以进行下一次加载
                oEl.removeAttr(sAttName);
                // 没有数据隐藏加载更多按钮
                !that.listHasNext && oEl.hide();
            });
        });
    }

    function fRenderMore(fCb) {
        var that = this;
        // 没有更多数据，不处理
        if (!that.listHasNext) {
            return;
        }
        that.requestData({
            uid: that.uid,
            page: that.page + 1,
            pageSize: that.pageSize,
            call: function (oResult) {
                // 是否有更多数据
                that.listHasNext = !!oResult.has_next && (oResult.images || []).length > 0;
                // 更新当前页面
                that.page++;
                // 渲染数据
                var image = oResult.images;
                var sHtml = '';
                $.each(oResult.images,function (nIndex, oImage) {
                    sHtml += that.tpl([
                        '<div>',
                        '<article class="mod">',
                            '<header class="mod-hd">',
                                '<time class="time">#{created_time}</time>',
                                '<a href="/profile/#{user_id}/" class="avatar">',
                                    '<img src="#{head_url}">',
                                '</a>',
                                '<div class="profile-info">',
                                    '<a title="#{username}" href="/profile/#{user_id}/">#{username}</a>',
                                '</div>',
                            '</header>',
                            '<div class="mod-bd">',
                                '<div class="img-box">',
                                    '<a href="/image/#{image_id}">',
                                    '<img src="#{image_url}?imageView2/1/h/290/w/290">',
                                    '</a>',
                                '</div>',
                            '</div>',
                        '<div class="mod-ft">',
                        '<ul class="discuss-list">',
                        '<li class="more-discuss">',
                        '<a>',
                        '<span>全部 </span><span class="">#{comments_count}</span>',
                        '<span> 条评论</span></a>',
                        '</li>',
                        '<li>',
                        '<a class=" icon-remove" title="删除评论"></a>',
                        '<a class="_4zhc5 _iqaka" title="#{username}" href="/profile/#{user_id}" data-reactid=".0.1.0.0.0.2.1.2:$comment-17856951190001917.1">#{username}</a>',
                        '<span>',
                        '<span>#{content}</span>',
                        '</span>',
                        '</li>',
                        '</ul>',
                        '<section class="discuss-edit">',
                        '<a class="icon-heart"></a>',
                        '<form>',
                        '<input placeholder="添加评论..." type="text">',
                        '</form>',
                        '<button class="more-info">更多选项</button>',
                        '</section>',
                        '</div>',
                        '</article>',
                        '</div>'].join(''), oImage);
                });
                sHtml && that.listEl.append(sHtml);
            },
            error: function () {
                alert('出现错误，请稍后重试');
            },
            always: fCb
        });
    }

    function fRequestData(oConf) {
        var that = this;
        var sUrl = '/index/'+ oConf.page + '/' + oConf.pageSize + '/';
        $.ajax({url: sUrl, dataType: 'json'}).done(oConf.call).fail(oConf.error).always(oConf.always);
    }

    function fTpl(sTpl, oData) {
        var that = this;
        sTpl = $.trim(sTpl);
        return sTpl.replace(/#{(.*?)}/g, function (sStr, sName) {
            return oData[sName] === undefined || oData[sName] === null ? '' : oData[sName];
        });
    }
});

$(function () {
    var oExports = {
        initialize: fInitialize,
        encode: fEncode
    };
    oExports.initialize();

    function fInitialize() {
        var that = this;
        var sImageId = window.imageId;
        var oCmtIpt = $('#jsCmt');
        var oListDv = $('ul.js-discuss-list');

        // 点击添加评论
        var bSubmit = false;
        $('#jsSubmit').on('click', function () {
            var sCmt = $.trim(oCmtIpt.val());
            // 评论为空不能提交
            if (!sCmt) {
                return alert('评论不能为空');
            }
            // 上一个提交没结束之前，不再提交新的评论
            if (bSubmit) {
                return;
            }
            bSubmit = true;
            $.ajax({
                url: '/addcomment/',
                type: 'post',
                dataType: 'json',
                data: {image_id: sImageId, content: sCmt}
            }).done(function (oResult) {
                if(oResult.code == 1) {
                    window.location = "/regloginpage/";
                }
                if (oResult.code !== 0) {
                    return alert(oResult.msg || '提交失败，请重试');
                }
                // 清空输入框
                oCmtIpt.val('');
                // 渲染新的评论
                var sHtml = [
                    '<li>',
                        '<a class="_4zhc5 _iqaka" title="', that.encode(oResult.username), '" href="/profile/', oResult.user_id, '">', that.encode(oResult.username), '</a> ',
                        '<span><span>', that.encode(sCmt), '</span></span>',
                    '</li>'].join('');
                oListDv.prepend(sHtml);
            }).fail(function (oResult) {
                alert(oResult.msg || '提交失败，请重试');
            }).always(function () {
                bSubmit = false;
            });
        });
    }

    function fEncode(sStr, bDecode) {
        var aReplace =["&#39;", "'", "&quot;", '"', "&nbsp;", " ", "&gt;", ">", "&lt;", "<", "&amp;", "&", "&yen;", "¥"];
        !bDecode && aReplace.reverse();
        for (var i = 0, l = aReplace.length; i < l; i += 2) {
             sStr = sStr.replace(new RegExp(aReplace[i],'g'), aReplace[i+1]);
        }
        return sStr;
    };

});