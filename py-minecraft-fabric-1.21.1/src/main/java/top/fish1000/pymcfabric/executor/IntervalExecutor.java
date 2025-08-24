package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.PriorityQueue;
import java.util.function.Consumer;
import java.util.function.IntSupplier;

public class IntervalExecutor<T>
        extends
        TimedExecutor<T, IntervalValue<Consumer<T>>, LinkedList<ExecutorIdentifier<IntervalValue<Consumer<T>>>>> {

    private final PriorityQueue<IntervalValue<Consumer<T>>> intervalScheduled = new PriorityQueue<>(
            (a, b) -> a.offset() - b.offset());

    public IntervalExecutor(IntSupplier tickSupplier) {
        super(tickSupplier, LinkedList::new);
    }

    public void push(int tick, int interval, Consumer<T> callback, TickType tickType) {
        int currentTick = tickSupplier.getAsInt();
        tick = tickType.convert(tick, currentTick);
        IntervalValue<Consumer<T>> val = new IntervalValue<>(interval, tick, callback);
        intervalScheduled.add(val);
        super.push(tick, val, TickType.ABSOLUTE);
    }

    public void tick(T data) {
        int currentTick = tickSupplier.getAsInt();
        for (int i = 0; i < intervalScheduled.size(); i++) {
            IntervalValue<Consumer<T>> val = intervalScheduled.poll();
            if (val.offset() <= currentTick) {
                val = val.step();
                super.push(val.offset(), val, TickType.ABSOLUTE);
                intervalScheduled.add(val);
            } else {
                intervalScheduled.add(val);
                break;
            }
        }
        super.tick(data);
    }
}
