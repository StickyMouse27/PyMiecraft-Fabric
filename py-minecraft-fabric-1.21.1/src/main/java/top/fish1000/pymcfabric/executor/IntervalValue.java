package top.fish1000.pymcfabric.executor;

import java.util.function.Supplier;

public record IntervalValue<T>(int interval, int offset, T value) implements Supplier<T> {
    public T get() {
        return value;
    }

    public boolean check(int tick) {
        return tick % interval == offset % interval;
    }

    public IntervalValue<T> step() {
        return new IntervalValue<>(interval, offset + interval, value);
    }
}