include "globals.mzn";


int: NUM_ACTIONS;
int: NUM_DRIVERS;
int: NUM_TRAINS;

%-------------------------------
array[1..NUM_ACTIONS] of int: D;                            % durations
array[1..NUM_ACTIONS] of 1..NUM_TRAINS: TA;                 % train assignments: which train does which task

%-------------------------------
int: TOTAL_DURATION = 2*sum(D)+1;                             % total duration

%-------------------------------
int: NUM_PRECEDENCE_CONSTRAINTS;
array[1..NUM_PRECEDENCE_CONSTRAINTS] of 1..NUM_ACTIONS: preceding;
array[1..NUM_PRECEDENCE_CONSTRAINTS] of 1..NUM_ACTIONS: anteceding;

int: NUM_SWITCH_CONSTRAINTS;
array[1..NUM_SWITCH_CONSTRAINTS] of 1..NUM_ACTIONS: before_switch;
array[1..NUM_SWITCH_CONSTRAINTS] of 1..NUM_ACTIONS: after_switch;

int: NUM_TURN_CONSTRAINTS;
array[1..NUM_TURN_CONSTRAINTS] of 1..NUM_ACTIONS: before_turn;
array[1..NUM_TURN_CONSTRAINTS] of 1..NUM_ACTIONS: after_turn;

int: MAX_WALKING;
array[1..NUM_ACTIONS, 1..NUM_ACTIONS] of 0..MAX_WALKING: walk_times;

%-------------------------------
array[1..NUM_ACTIONS] of var 1..TOTAL_DURATION: S;          % start times
array[1..NUM_ACTIONS] of var 1..NUM_DRIVERS: DA;            % driver assignments
var 1..TOTAL_DURATION: end;                                 % total end time
%-------------------------------

% precedence constraints
constraint forall (p in 1..NUM_PRECEDENCE_CONSTRAINTS)(
    (S[preceding[p]] + D[preceding[p]]) <= S[anteceding[p]]
);

% switch constraints
constraint forall (sw in 1..NUM_SWITCH_CONSTRAINTS)(
    (S[before_switch[sw]] + D[before_switch[sw]]) < (S[after_switch[sw]])
);

% turn constraints
constraint forall (tc in 1..NUM_TURN_CONSTRAINTS)(
    (S[before_turn[tc]] + D[before_turn[tc]]) < (S[after_turn[tc]] - 2)
);


% redundant constraint: strict precedence implies non overlap
constraint forall (p in 1..NUM_PRECEDENCE_CONSTRAINTS)(
    disjunctive(
        [S[preceding[p]], S[anteceding[p]]],
        [D[preceding[p]], D[anteceding[p]]]
    )
);

% redundant constraint: switch inbetween implies non overlap
constraint forall (sw in 1..NUM_SWITCH_CONSTRAINTS)(
    disjunctive(
        [S[before_switch[sw]], S[after_switch[sw]]],
        [D[before_switch[sw]], D[after_switch[sw]]]
    )
);

% redundant constraint: turn inbetween implies non overlap
constraint forall (tc in 1..NUM_TURN_CONSTRAINTS)(
    disjunctive(
        [S[before_turn[tc]], S[after_turn[tc]]],
        [D[before_turn[tc]], D[after_turn[tc]]]
    )
);


% if the the driver needs to change train, or the train
% needs to change diver add a gap in the schedule
constraint forall (a1 in 1..(NUM_ACTIONS-1))(
    forall (a2 in (a1+1)..NUM_ACTIONS)(
        if (
            (D[a1] < 30 /\ D[a2] < 30) /\
            (DA[a1] = DA[a2] /\ TA[a1] != TA[a2])
        ) then (
            ((S[a1] + D[a1]) < (S[a2] - 3 - walk_times[a1,a2]))
            \/ ((S[a2] + D[a2]) < (S[a1] - 3 - walk_times[a2,a1]))
        )
        endif
    )    
);

constraint forall (a1 in 1..(NUM_ACTIONS-1))(
    forall (a2 in (a1+1)..NUM_ACTIONS)(
        if (
            (D[a1] < 30 /\ D[a2] < 30) /\
            (DA[a1] != DA[a2] /\ TA[a1] = TA[a2])
        ) then (
            ((S[a1] + D[a1]) < (S[a2] - 3))
            \/ ((S[a2] + D[a2]) < (S[a1] - 3))
        )
        endif
    )    
);

constraint symmetry_breaking_constraint(
    DA[1] = 1
);

constraint symmetry_breaking_constraint(
    S[1] = 5
);

% objective
constraint forall(i in 1..NUM_ACTIONS)(
    S[i] + D[i] <= end
);


solve 
::int_search(S, smallest, indomain_min)
minimize end;

output(
        [
            show(S),
            show(D),
            show(DA),
            show(TA),
        ]
);
