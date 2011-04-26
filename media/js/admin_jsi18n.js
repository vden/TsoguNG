
/* gettext library */

var catalog = new Array();

function pluralidx(count) { return (count == 1) ? 0 : 1; }
catalog['6 a.m.'] = '6 \u0447\u0430\u0441\u043e\u0432';
catalog['Add'] = '\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c';
catalog['Available %s'] = '\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 %s';
catalog['Calendar'] = '\u041a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u044c';
catalog['Cancel'] = '\u041e\u0442\u043c\u0435\u043d\u0430';
catalog['Choose a time'] = '\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0432\u0440\u0435\u043c\u044f';
catalog['Choose all'] = '\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u0432\u0441\u0435';
catalog['Chosen %s'] = '\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 %s';
catalog['Clear all'] = '\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c \u0432\u0441\u0451';
catalog['Clock'] = '\u0427\u0430\u0441\u044b';
catalog['Hide'] = '\u0421\u043a\u0440\u044b\u0442\u044c';
catalog['January February March April May June July August September October November December'] = '\u042f\u043d\u0432\u0430\u0440\u044c \u0424\u0435\u0432\u0440\u0430\u043b\u044c \u041c\u0430\u0440\u0442 \u0410\u043f\u0440\u0435\u043b\u044c \u041c\u0430\u0439 \u0418\u044e\u043d\u044c \u0418\u044e\u043b\u044c \u0410\u0432\u0433\u0443\u0441\u0442 \u0421\u0435\u043d\u0442\u044f\u0431\u0440\u044c \u041e\u043a\u0442\u044f\u0431\u0440\u044c \u041d\u043e\u044f\u0431\u0440\u044c \u0414\u0435\u043a\u0430\u0431\u0440\u044c';
catalog['Midnight'] = '\u041f\u043e\u043b\u043d\u043e\u0447\u044c';
catalog['Noon'] = '\u041f\u043e\u043b\u0434\u0435\u043d\u044c';
catalog['Now'] = '\u0421\u0435\u0439\u0447\u0430\u0441';
catalog['Remove'] = '\u0423\u0434\u0430\u043b\u0438\u0442\u044c';
catalog['S M T W T F S'] = '\u0412 \u041f \u0412 \u0421 \u0427 \u041f \u0421';
catalog['Select your choice(s) and click '] = '\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0438 \u043d\u0430\u0436\u043c\u0438\u0442\u0435 ';
catalog['Show'] = '\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c';
catalog['Sunday Monday Tuesday Wednesday Thursday Friday Saturday'] = '\u0412\u043e\u0441\u043a\u0440\u0435\u0441\u0435\u043d\u044c\u0435 \u041f\u043e\u043d\u0435\u0434\u0435\u043b\u044c\u043d\u0438\u043a \u0412\u0442\u043e\u0440\u043d\u0438\u043a \u0421\u0440\u0435\u0434\u0430 \u0427\u0435\u0442\u0432\u0435\u0440\u0433 \u041f\u044f\u0442\u043d\u0438\u0446\u0430 \u0421\u0443\u0431\u0431\u043e\u0442\u0430';
catalog['Today'] = '\u0421\u0435\u0433\u043e\u0434\u043d\u044f';
catalog['Tomorrow'] = '\u0417\u0430\u0432\u0442\u0440\u0430';
catalog['Yesterday'] = '\u0412\u0447\u0435\u0440\u0430';


function gettext(msgid) {
  var value = catalog[msgid];
  if (typeof(value) == 'undefined') {
    return msgid;
  } else {
    return (typeof(value) == 'string') ? value : value[0];
  }
}

function ngettext(singular, plural, count) {
  value = catalog[singular];
  if (typeof(value) == 'undefined') {
    return (count == 1) ? singular : plural;
  } else {
    return value[pluralidx(count)];
  }
}

function gettext_noop(msgid) { return msgid; }

function interpolate(fmt, obj, named) {
  if (named) {
    return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
  } else {
    return fmt.replace(/%s/g, function(match){return String(obj.shift())});
  }
}
