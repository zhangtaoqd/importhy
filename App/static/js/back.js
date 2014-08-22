/**
 * Created by zhangtao on 14-2-18.
 */
//******转换对象为可提交json对象***********

sy.transObjectToDjangoAjax = function (o) {
    if ($.isPlainObject(o) || $.isArray(o)) {
        if (sy.isBasicType(o)) {
            if ($.isArray(o)) {
                return JSON.stringify(o);
            }
            if ($.isPlainObject(o)) {
                return o;
            }
        } else {
            if ($.isArray(o)) {
                for (var i = 0, ilen = o.length; i < ilen; i++) {
                    var y = sy.transObjectToDjangoAjax(o[i]);
                    if (y != null)
                        o[i] = y;
                }
                return JSON.stringify(o);
            }

            if ($.isPlainObject(o)) {
                for (var p in o) {
                    var y = sy.transObjectToDjangoAjax(o[p]);
                    if (y != null) {
                        o[p] = y;
                    }
                }
                return o;
            }
        }
    }
    else {
        return o;
    }
}

sy.isBasicType = function (o) {  //o不包含对象或数组返回true
    var t = true;
    $.each(o, function (key, value) {
        if ($.isPlainObject(value) || $.isArray(value)) {
            t = false;
            return false;
        }
    });
    return t;
}

