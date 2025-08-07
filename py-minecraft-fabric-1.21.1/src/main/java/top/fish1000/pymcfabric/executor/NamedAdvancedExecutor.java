package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.IntSupplier;

import top.fish1000.pymcfabric.Utils;

public class NamedAdvancedExecutor<T> extends NamedExecutor<T> {

    protected final List<NamedValue<Consumer<T>>> callbackContinuousList;
    protected final List<NamedValue<Consumer<T>>> callbackOnceList;

    public NamedAdvancedExecutor(IntSupplier tickSupplier) {
        super(tickSupplier);
        callbackContinuousList = new LinkedList<>();
        callbackOnceList = new LinkedList<>();
    }

    @Override
    public void tick(T data, String name) {
        // Utils.LOGGER.info("Looking for callback: tick{} @ {}", tickSupplier.get(),
        // name);
        super.tick(data, name);
        callbackContinuousList.forEach(callback -> {
            if (callback.name().equals(name)) {
                Utils.LOGGER.info("Found callback(continuous)");
                callback.value().accept(data);
            }
        });
        callbackOnceList.forEach(callback -> {
            if (callback.name().equals(name)) {
                callback.value().accept(data);
                Utils.LOGGER.info("Found callback(once), removed");
            }
        });
        callbackOnceList.removeIf(namedValue -> namedValue.name().equals(name));
    }

    public void pushScheduled(int tick, Consumer<T> callback, String name) {
        Utils.LOGGER.info("Pushing callback(scheduled): tick{} @ {}", tickSupplier.getAsInt(), name);
        super.push(tick, callback, name, TickType.RELATIVE);
    }

    public void pushOnce(Consumer<T> callback, String name) {
        Utils.LOGGER.info("Pushing callback(once): tick{} @ {}", tickSupplier.getAsInt(), name);
        callbackOnceList.add(new NamedValue<>(callback, name));
    }

    public void pushContinuous(Consumer<T> callback, String name) {
        Utils.LOGGER.info("Pushing callback(continuous): tick{} @ {}", tickSupplier.getAsInt(), name);
        callbackContinuousList.add(new NamedValue<>(callback, name));
    }
}
