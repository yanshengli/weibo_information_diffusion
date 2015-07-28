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
var /* method vars */
	r = /%\+?(\d+\$)?(0|'.)?(-)?(\d+)?(\.\d+)?(.)/g;

module.exports = function(str) {
	var value,
		index = 1,
		execMatch,
		tempVar1,
		tempVar2;
	while (execMatch = r.exec(str)) {
		value = execMatch[6];
		if (value == "s") {

			// arg from index
			if ((value = execMatch[1]) && value[(tempVar1 = value.length - 1)] == "$") {
				value = value.substr(0, tempVar1);
			}
			value=arguments[value || index]+'';

			// pad char
			if (tempVar1 = execMatch[2]) {
				if (tempVar1[0] == "'") {
					tempVar1 = tempVar1[1];
				}
			} else {
				tempVar1 = ' ';
			}
			if (tempVar2 = execMatch[4]) while (value.length < tempVar2) {
				value = execMatch[3] ? (value + tempVar1) : (tempVar1 + value);
			}

			// cutoff
			if ((tempVar1 = execMatch[5] && execMatch[5].substr(1)) && value.length > tempVar1) {
				value = execMatch[3] ? value.substr(0, tempVar1) : value.substr(value.length - tempVar1);
			}
			index++;
		}
		str = str.substr(0, tempVar1 = execMatch.index) + value + str.substr(r.lastIndex);
		r.lastIndex = value.length + tempVar1;
	}
	return str;
};