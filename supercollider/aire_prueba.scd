
(
Server.local.waitForBoot({
	(
		z.free;
		z = Buffer.alloc(s, 512, 1);
		z.sine1(1.0 / [1, 2, 3, 4], true, true, true);

		{
			loop {
				SynthDef("g1",{ arg out=0, bufnum=0, dur=1, rate=1, pos=0, sdens=1, edens=1;

					var env, trig, dens, snd;

					dens = Line.kr(sdens,edens,dur);
					trig = [LFNoise0,SinOsc,Impulse,LFPulse,LFSaw].choose.postln;
					trig = trig.ar(Line.kr(sdens,edens,dur));
					env = Env.perc(
						attackTime: rrand(0.1, 1),
						releaseTime: dur * rrand(0.5, 1),
						curve: -1).kr;

					snd = GrainBuf.ar(2,trig,1/dens,bufnum,rate,pos)*env;
					snd = [LPF, HPF].choose.ar(
						in: snd,
						freq: LFNoise2.kr(rrand(0.5, 4)).range(100, 1000)
					);
					snd = FreeVerb.ar(
						in: snd,
						mix: 0.4,
						room: 0.9,
						damp: 0.9,
						mul: 1
					) * Env.linen(0, dur+1, 1, 0.5).kr(doneAction: 2);

					snd = Limiter.ar(snd);

					Out.ar(out, snd);
				}).add;

				[1,2,4,8,16,32].choose.postln.wait;
			}
		}.fork;


		a = Pbind(
			\instrument, \g1,
			\dur, Pseq([
				Pseq([0.5, 0.1], 8),
				Pseq([0.25, 0.125, 0.125], 8),
				Pseq([0.125, 0.1], 8)
			],inf),
			\sdens, Pseq([9000,1000,500], inf),
			\edens,Prand([
				Pseq([900,1000,500]/10,4),
				Pseq([1, 2], 1)
			],inf),
			\rate, Pwhite(-10.0, 1),
			\pos,Pwhite(0.0, 1),
			\bufnum,z.bufnum
		);

		b = Pbind(
			\instrument,\g1,
			\dur,Pseq([4, 5, 6],inf),
			\sdens,Pseq([1,10,5],inf),
			\edens,Prand([
				Pseq([9000,10,50], 1),
				Pseq([1, 0.1], 3)
			],inf),
			\rate, Pwhite(1, 3),
			\pos,Pwhite(-10.0, 10),
			\bufnum,z.bufnum
		);

		c = Pbind(
			\instrument,\g1,
			\dur,Prand([1/2, Rest(4)],inf),
			\sdens,Pseq([900,1000,500,25],inf),
			\edens,Prand([
				Pseq([9000,1000,500,25],1),
				Pseq([1],4)
			],inf),
			\rate, Pwhite(-2, -1),
			\pos,Pwhite(-10, 10.0),
			\bufnum,z.bufnum
		);


		a.play;
		b.play;
		c.play;
	)
});
)


(
f = OSCFunc( { | msg, time, addr, port |
	var pyFreq,pyNharm,pyDetune,pyOut;
	pyFreq = msg[1]+1*30; //valores originales del 0 al 5
	pyNharm = msg[2]; //valores originales del 1 al 30
	pyDetune = msg[3]/2.5;//valores originales del 1 al 100 milisegundos
	pyOut = msg[4];//valores originales del 1 al 8
	( "/raspi1/freq is " + pyFreq ).postln;
	( "/raspi1/nharm " + pyNharm ).postln;
	( "/raspi1/detune " + pyDetune ).postln;
	//( "/raspi1/channel is " + pyOut).postln;
	e.set(\freq,pyFreq, \nharm,pyNharm, \detune,pyDetune,
		 );
}, '/raspi1/' );
)