// Independent serialization regression over every permitted slider position.
const assert=require('node:assert/strict');
const {toRatio}=require('../cautum/static/rates.js');
let count=0;
for(const [lo,hi,step] of [[40,90,1],[2,25,.5],[2,40,.1],[10,75,.5]]){
  for(let i=0;i<=Math.round((hi-lo)/step);i++){
    const value=(lo+i*step).toFixed(1),ratio=toRatio(value),encoded=JSON.stringify(ratio);
    assert.ok(ratio>=0&&ratio<=1);
    assert.ok(!encoded.includes('.')||encoded.split('.')[1].length<=6,encoded);
    assert.equal(Math.round(ratio*1000000),Math.round(Number(value)*10000));count++;
  }
}
assert.equal(toRatio('12.3'),.123);
for(const invalid of ['NaN','Infinity','-1','101',''])assert.throws(()=>toRatio(invalid));
console.log(`${count} slider positions serialize within the six-decimal ratio contract; invalid inputs reject.`);
