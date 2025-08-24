package top.fish1000.pymcfabric.executor;

import java.util.function.Supplier;

public class ExecutorIdentifier<T> implements Supplier<T> {
    private static int id_suppllier = 0;

    protected int getId() {
        return id_suppllier++;
    }

    public final T data;
    public final int id;

    public ExecutorIdentifier(T data) {
        this.data = data;
        this.id = getId();
    }

    public static <T> ExecutorIdentifier<T> of(T data) {
        return new ExecutorIdentifier<>(data);
    }

    @Override
    public T get() {
        return data;
    }
}
