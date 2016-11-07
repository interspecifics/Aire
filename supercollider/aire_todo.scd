//* Aire. Casa del Lago 2016

//inicio
(
o = Server.local.options; ////variable para cambios en el servidor
o.numOutputBusChannels = 8; //setea 8 canales 8 de salida ANTES DE BOOTEAR!!
o.numOutputBusChannels.postln;/// imprime canales de salida habilitados
o.device = "MOTU 828mk3 Hybrid"; //setea tarjeta de audio
o.outDevice.postln; //imprimir dispositivo de salida
s.boot; ///bootear servidos
)


////ESTACIÓN MIGUEL HIDALGO

(
SynthDef(\miguelhidalgo,{
	arg mghfreq=40, nharm=10, detune=0.5,amp=0.4,out=0;
	var sig, env;
	env = EnvGen.kr(Env.adsr(0.5,0.5,0.5,1),doneAction:2);
	sig = Blip.ar(
		mghfreq *
		LFNoise1.kr(0.2!8).bipolar(detune.neg,detune).midiratio,nharm);
	sig = sig * LFNoise1.kr(0.4!8).exprange(0.1,1);
	sig = (sig * env * amp);
	Out.ar(out,sig);

}).add;
)

a = Synth.new(\miguelhidalgo);
a.set(\amp,4);
a.free;

(
b = OSCFunc( { | msg, time, addr, port |
	var mghFreq;
	mghFreq = msg[1].asFloat;
	( "MGH value is " + mghFreq ).postln;
	a.set(\mghfreq,mghFreq
		 );
}, '/MGH' );
)

b.free;

////ESTACIÓN CAMARONES

(
SynthDef(\camarones,{
	arg freq1=200,freq2=300, gate=1, dur=100, amp=0.5,out=0, pospan=2.0, width=2.0;
	var env,sig, panaz;
	env = EnvGen.kr(Env.perc(1/20,dur), gate);
	sig =  SinOsc.ar(BrownNoise.ar(freq1, freq2));
	sig = sig * amp * env;
	panaz= PanAz.ar(8,sig,pospan,0.3,width,0.5);
	Out.ar(out,panaz);
}).add;
)


c=Synth(\camarones, [\Freq1,rrand(100,300),\freq2,rrand(200,400)]);
c.set(\amp, 4);
c.free;


(
d= OSCFunc( { | msg, time, addr, port |
	var freq;
	freq = msg[1].asFloat;
	( "ACO value is " + freq ).postln;
	c.set(\freq1,freq
				);
}, '/ACO' );
)

d.free;


////ESTACIÓN ACATLÁN
(
SynthDef(\panaz2, {
	arg noise=0.3, width = 2.0;
    var panaz;
	panaz = PanAz.ar(
        8,
        ClipNoise.ar,
        LFSaw.kr(LFNoise1.kr(noise)),0.01,width,0.5);
	Out.ar(0,panaz);
}).add
)
e=Synth(\panaz2);
e.set(\noise,2);
e.set(\width,1);
e.free;

(
f= OSCFunc( { | msg, time, addr, port |
	var noise;
	noise = msg[1].asFloat;
	( "FAC value is " + noise ).postln;
	e.set(\noise,noise
				);
}, '/FAC' );
)

f.free

////ESTACIÓN CUAJIMALPA

(
SynthDef.new(\pulses, {
	arg ampHz=2, fund=10, maxPartial=10, width=0.5;
	var amp1, amp2, freq1, freq2, sig1, sig2,mixer;
	amp1 = LFPulse.kr(ampHz, 0, 0.12) * 0.1;
	amp2 = LFPulse.kr (ampHz, 0.5, 0.12) * 0.1;
	freq1 = LFNoise0.kr(4).exprange(fund, fund*maxPartial).round(fund);
	freq2 = LFNoise0.kr(4).exprange(fund, fund*maxPartial).round(fund);
	freq1 = freq1 * LFPulse.kr(8, add:1);
	freq2 = freq2 * LFPulse.kr(6, add:1);
	sig1 = Pulse.ar(freq1, width, amp1);
	sig2 = Pulse.ar (freq2, width, amp2);
	sig1 = FreeVerb.ar(sig1, 0.7, 0.8, 0.25);
	sig2 = FreeVerb.ar(sig2, 0.7, 0.8, 0.25);
	mixer = Mix.new([sig1,sig2!8]);
	Out.ar (0, mixer);
}).add;
)
g = Synth.new(\pulses);
g.free;

(
h = OSCFunc( { | msg, time, addr, port |
	var maxPartial;
	maxPartial = msg[1].asFloat;
	( "CUA value is " + maxPartial ).postln;
	g.set(\maxPartial,maxPartial
		);
}, '/CUA' );
)
h.free


////ESTACION BENITO JUAREZ


(
    ~buf2= Buffer.alloc(s, 512,1);
	~buf2.sine1(1/Array.fill(10,{|i| i+1}));

SynthDef(\drone1, {|out= 0, gate= 1, amp= 0.15,
modFreq=1, freq1=64, freq2=65, mul1=0.09, mul2=0.09|
	var env, mod, a, b, mixer;
	env = EnvGen.ar(Env.asr(0.01, 1, 0.5), gate, doneAction:2);
	mod = LFTri.ar(modFreq);
	a = Osc.ar (~buf2, freq1,  mod, mul1)!8;
	b = Osc.ar (~buf2, freq2, mod,  mul2)!8;
	mixer= Mix.new([a,b]);
	Out.ar(out, mixer * (env *amp));
}).add;
)


i = Synth(\drone1);
i.set(\amp,1);
i.free;

(
j = OSCFunc( { | msg, time, addr, port |
	var pymodFreq;
	pymodFreq = msg[1];
	( "BJU value is " + pymodFreq ).postln;
	i.set(\modFreq,pymodFreq
		 );
}, '/BJU' );
)
j.free
)






