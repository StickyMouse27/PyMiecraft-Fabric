package top.fish1000.pymcfabric.executor;

public class NamedExecutorIdentifier<T> extends ExecutorIdentifier<T> {
    public final String name;

    public NamedExecutorIdentifier(T data, String name) {
        super(data);
        this.name = name;
    }
}
