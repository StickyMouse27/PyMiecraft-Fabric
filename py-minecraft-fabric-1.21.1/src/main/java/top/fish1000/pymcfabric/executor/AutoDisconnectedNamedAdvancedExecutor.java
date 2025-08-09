package top.fish1000.pymcfabric.executor;

import java.util.function.IntSupplier;

public class AutoDisconnectedNamedAdvancedExecutor<T> extends NamedAdvancedExecutor<T> {
    protected final Runnable disconnectCallback;

    public AutoDisconnectedNamedAdvancedExecutor(IntSupplier tickSupplier, Runnable disconnectCallback) {
        super(tickSupplier);
        this.disconnectCallback = disconnectCallback;
    }

    @Override
    public void tick(T data, String name) {
        super.tick(data, name);
        if (callbackOnceList.isEmpty() && callbackContinuousList.isEmpty() && callbackScheduled.isEmpty()) {
            disconnectCallback.run();
        }
    }
}
