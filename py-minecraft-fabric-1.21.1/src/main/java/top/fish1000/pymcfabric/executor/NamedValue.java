package top.fish1000.pymcfabric.executor;

import java.util.function.Supplier;

public record NamedValue<T>(T value, String name) implements Supplier<T> {
    public T get() {
        return value;
    }
}
