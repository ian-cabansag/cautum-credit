/* Normalize browser percentage controls to the backend's six-place ratio contract. */
(function(root){
  'use strict';
  function toRatio(percent){
    if(typeof percent!=='string'||!/^\d+(\.\d+)?$/.test(percent)||Number(percent)>100)throw Error('Rate control must be between 0 and 100 percent.');
    return Number((Number(percent)/100).toFixed(6));
  }
  if(typeof module==='object'&&module.exports)module.exports={toRatio};
  else root.CautumRates={toRatio};
})(typeof window==='undefined'?globalThis:window);
