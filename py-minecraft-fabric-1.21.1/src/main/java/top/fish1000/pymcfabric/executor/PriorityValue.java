package top.fish1000.pymcfabric.executor;

import java.util.function.Supplier;

public record PriorityValue<T>(int priority, T value) implements Supplier<T> {
    public T get() {
        return value;
    }
}