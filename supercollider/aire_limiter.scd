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


////PM2 Particulate matter 2.5 micrometers or less in diameter. City Hourly Average

(
SynthDef(\pm2,{
	arg mghfreq=40, nharm=10, detune=0.5,amp=2,out=0;
	var sig, env, limiter;
	env = EnvGen.kr(Env.adsr(0.5,0.5,0.5,1),doneAction:2);
	sig = Blip.ar(
		mghfreq *
		LFNoise1.kr(0.2!8).bipolar(detune.neg,detune).midiratio,nharm);
	sig = sig * LFNoise1.kr(0.4!8).exprange(0.1,1);
	sig = (sig * env * amp);
	limiter = Limiter.ar(sig,3,0.1);
	Out.ar(out,limiter);

}).add;
)

a = Synth.new(\pm2);
a.set(\amp,1);
a.free;

(
b = OSCFunc( { | msg, time, addr, port |
	var mghFreq,mghFreq1;
	mghFreq = msg[1].asFloat.linlin(0.1, 400.00, 40.00,100.00);
	mghFreq1 = msg[1].asFloat;
	( "pm2synth " + mghFreq ).postln;
	( "pm2value is " + mghFreq1 ).postln;
	a.set(\mghfreq,mghFreq
		 );
}, '/pm2' );
)

b.free;

////NITROGEN OXIDE LEVEL.City Hourly Average

(
SynthDef(\nitrogenoxide,{
	arg freq1=200,freq2=300, gate=1, dur=100, amp=0.3,out=0, pospan=2.0, width=2.0;
	var env,sig, panaz;
	sig =  SinOsc.ar(BrownNoise.ar(freq1, freq2));
	sig = sig * amp * env;
	panaz= PanAz.ar(8,sig,pospan,0.3,width,0.5);
	Out.ar(out,panaz);
}).add;
)


c=Synth(\nitrogenoxide, [\Freq1,rrand(100,200),\freq2,rrand(200,300)]);
c.set(\amp,0.5);
c.set(\width, 0);
c.free;


(
d= OSCFunc( { | msg, time, addr, port |
	var width,width1;
	width = msg[1].asFloat.linlin(10, 150.00, 0,10.00);
	width1 = msg[1].asFloat;
	( "NOXsynth width " + width ).postln;
	( "NOXvalue is " + width1 ).postln;
	c.set(\width,width
		 );
}, '/nox' );
)

d.free;


////SULFUR DIOXIDE.City Hourly Average
(
SynthDef(\panaz2, {
	arg noise=0.3, width = 2.0;
    var panaz;
	panaz = PanAz.ar(
        8,
        BrownNoise.ar,
        LFSaw.kr(LFNoise1.kr(noise)),0.05,width,0.5);
	Out.ar(0,panaz);
}).add
)
e=Synth(\panaz2);
e.set(\noise,1);
e.set(\width,1);
e.free;

(
f= OSCFunc( { | msg, time, addr, port |
	var noise;
	noise = msg[1].asFloat.linlin(0.1,100,0.1,5);
	( "so2 value is " + noise ).postln;
	e.set(\noise,noise
				);
}, '/so2' );
)

f.free

////CARBON MONOXIDE. City Hourly Average

(
SynthDef.new(\pulses, {
	arg ampHz=1, fund=0.009, maxPartial=1000, width=0.5;
	var amp1, amp2, freq1, freq2, sig1, sig2,mixer, limiter;
	amp1 = Pulse.kr(ampHz, 0, 0.12) * 0.5;
	amp2 = Pulse.kr (ampHz, 0.5, 0.12) * 0.5;
	freq1 = LFNoise1.kr(1).exprange(fund, fund*maxPartial).round(fund);
	freq2 = LFNoise1.kr(1).exprange(fund, fund*maxPartial).round(fund);
	freq1 = freq1 * SinOsc.kr(1, add:1);
	freq2 = freq2 * SinOsc.kr(1, add:1);
	sig1 = Pulse.ar(freq1, width, amp1);
	sig2 = Pulse.ar (freq2, width, amp2);
	sig1 = FreeVerb.ar(sig1, 0.7, 0.8, 0.25);
	sig2 = FreeVerb.ar(sig2, 0.7, 0.8, 0.25);
	mixer = Mix.new([sig1,sig2!8]);
	limiter = Limiter.ar(mixer,2,0.05);
	Out.ar (0, limiter);
}).add;
)
g = Synth.new(\pulses);
g.set(\ampHz,100);
g.free;

(
h = OSCFunc( { | msg, time, addr, port |
	var ampHz,ampHz1;
	ampHz = msg[1].asFloat.linlin(0.1,100,1,1000);
	ampHz1 = msg[1].asFloat;
	( "co synth " + ampHz ).postln;
	( "co value " + ampHz1 ).postln;
	g.set(\ampHz,ampHz
		);
}, '/co' );
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
i.set(\modFreq,0.5);
i.set(\freq1,40);
i.set(\freq2,70);

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






