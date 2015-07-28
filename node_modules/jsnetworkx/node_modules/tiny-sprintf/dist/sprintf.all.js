/**
 * sprintf implementation. Get pretty indented monospace strings.
 * @param {String} str - the string to parse
 * @param {...*} args - arguments, used in order, or referenced by n$
 * @returns {String}
 * @example
 * // Type casting...
 * sprintf('%s', 10); // '10'
 * sprintf('%s', 'abc'); // 'abc'
 *
 * // Escape anything else
 * sprintf('%%', 1); // '%'
 * sprintf('%T', 'abc'); // 'T'
 *
 * // Limit length
 * sprintf("%.5s", 'abcdef'); // 'bcdef'
 * sprintf("%-.5s", 'abcdef'); // 'abcde'
 *
 * // Indent to length
 * sprintf("%5s", 'a'); // '    a'
 * sprintf("%-5s", 'a'); // 'a    '
 * sprintf("%5.4s", 'abc'); // ' abc'
 * sprintf("%-5.4s", 'abc'); // 'abc '
 *
 * // Use pad chars
 * sprintf("%04s", 10); // "0010"
 * sprintf("%'#4s", 10); // "##10"
 *
 * // Use arguments in order
 * sprintf("%1$s, %2$s, %2$s, %1$s!", 'left', 'right'); // 'left, right, right, left!'
 */

var undefined,
	/* method vars */
	r = /%(\+)?(\d+\$)?(0|'.)?(-)?(\d+)?(\.\d+)?(.)/g,
	s = function(str) {
		var value,
			index = 1,
			execMatch,
			tempVar1,
			tempVar2,
			tempVar3;
		while (execMatch = r.exec(str)) {
			value = execMatch[7];

			// arg from index
			if ((tempVar2 = execMatch[2]) && tempVar2[(tempVar1 = tempVar2.length - 1)] == "$") {
				tempVar2 = tempVar2.substr(0, tempVar1);
			}

			if (s[tempVar1 = value.toLowerCase()] &&
				(tempVar3 = s[tempVar1](arguments[tempVar2 || index], /[A-Z]/.test(value), execMatch[1])) !== undefined) {

				value=''+tempVar3;

				// pad char
				if (tempVar1 = execMatch[3]) {
					if (tempVar1[0] == "'") {
						tempVar1 = tempVar1[1];
					}
				} else {
					tempVar1 = ' ';
				}
				if (tempVar2 = execMatch[5]) while (value.length < tempVar2) {
					value = execMatch[4] ? (value + tempVar1) : (tempVar1 + value);
				}

				if ((tempVar1 = execMatch[6] && execMatch[6].substr(1)) && value.length > tempVar1) {
					value = execMatch[4] ? value.substr(0, tempVar1) : value.substr(value.length - tempVar1);
				}
				index++;
			}
			str = str.substr(0, tempVar1 = execMatch.index) + value + str.substr(r.lastIndex);
			r.lastIndex = value.length + tempVar1;
		}
		return str;
	};

/**
 * Typecasts to number, returns as byte string
 * @param {*} value
 * @param {Boolean} caps
 * @returns {String|undefined}
 */
s.b=function(value, caps) {
	return caps ? undefined : (+value).toString(2);
};
/**
 * Typecasts to number, then returns the equivalent ASCII char code.
 * @param {*} value
 * @param {Boolean} caps
 * @returns {String|undefined}
 */
s.c=function(value, caps) {
	return caps ? undefined : String.fromCharCode(+value);
};
/**
 * Typecasts to number, adds plus char if desired.
 * @param {*} value
 * @param {Boolean} caps
 * @param {String} [plusChar]
 * @returns {String|undefined}
 */
s.d=function(value, caps, plusChar) {
	return caps ? undefined : (plusChar || '') + (+value);
};
/**
 * Typecasts to number, then return 'scientific notation' (toExponential)
 * @param {*} value
 * @param {Boolean} caps
 * @returns {String|undefined}
 */
s.e=function(value, caps) {
	value = (+value).toExponential();
	return caps ? value.toUpperCase() : value;
};
/**
 * Typecasts to number, then returns locale aware format (toLocaleString).
 * @param {*} value
 * @returns {string}
 */
s.f=function(value) {
	return (+value).toLocaleString();
};
/**
 * Does f or e, depending on the size of value.
 * Between <code>131071</code> and <code>-131072</code>, f is done. Outside, e.
 * Based on a preset bitshift action.
 * @param value
 * @param caps
 * @returns {String|undefined}
 */
s.g=function(value, caps) {
	var v1 = (+value).toExponential(),
		v2 = (+value).toLocaleString();
	value = (v1.length < v2.length) ? v1 : v2;
	return caps ? value.toUpperCase() : value;
};
/**
 * Typecasts to number, then returns octal string
 * @param {*} value
 * @param {Boolean} caps
 * @returns {String|undefined}
 */
s.o=function(value, caps) {
	return caps ? undefined : (+value).toString(8);
};
/**
 * Returns string value only if lowercase s.
 * @param {*} value
 * @param {Boolean} caps
 * @returns {String|undefined}
 */
s.s=function(value, caps) {
	return caps ? undefined : value+'';
};
/**
 * Typecasts to number, then returns hexadecimal string
 * @param {*} value
 * @param {Boolean} caps
 * @returns {String|undefined}
 */
s.x=function(value, caps) {
	value = (+value).toString(16);
	if (caps) {
		value = value.toUpperCase();
	}
	return value
};

module.exports = s;