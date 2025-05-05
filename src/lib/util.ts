export const hiraToKata = (word: string) => {
  const hira = "あいうえおぁぃぅぇぉゔかきくけこがぎぐげごさしすせそざじずぜぞたちつてとっだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよゃゅょらりるれろわをん".split("");
  const kata = "アイウエオァィゥェォヴカキクケコガギグゲゴサシスセソザジズゼゾタチツテトッダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨャュョラリルレロワヲン".split("");
  let result = word;
  for (let i = 0; i < hira.length; i++) {
    result = result.replace(new RegExp(hira[i], "g"), kata[i]);
  }
  return result;
};